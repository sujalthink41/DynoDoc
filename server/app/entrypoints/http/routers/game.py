"""Gamification routes — DynoCoin wallet, Connections game, and the leaderboard."""

import secrets
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.gamification import connections as conn
from app.domains.gamification import rewards as merch
from app.domains.gamification.dtos import (
    CoinTxnView,
    ConnectionsResult,
    ConnectionsView,
    ConnGroupView,
    DailyBonusView,
    DailySettleAward,
    DailySettleView,
    LeaderboardEntry,
    LeaderboardView,
    PlayerView,
    RedemptionView,
    RewardsView,
    RewardView,
)
from app.domains.gamification.models import GamePlay
from app.domains.gamification.repository import (
    CONNECTIONS_REWARD,
    EXTRA_COURSE_COST,
    add_play,
    award_coins,
    bump_streak,
    buy_course_slot,
    daily_leaderboard,
    daily_play_rank,
    daily_visit_bonus,
    get_or_create_profile,
    get_play,
    leaderboard_top,
    list_recent_txns,
    list_redemptions,
    player_rank,
    redeem_reward,
    settle_daily_leaderboard,
    to_player_view,
    to_txn_view,
)
from app.domains.user.models import User
from app.entrypoints.http.deps import db_session, require_principal
from app.entrypoints.http.schemas.connections import ConnectionsAttemptRequest
from app.entrypoints.http.schemas.reward import RedeemRequest
from app.runtime.settings import Settings, get_settings
from app.shared.errors import (
    ConflictError,
    DependencyUnavailableError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

router = APIRouter(prefix="/game", tags=["gamification"])


def _display_name(user: User) -> str:
    return user.display_name or user.email


@router.get("/profile", response_model=PlayerView)
async def get_profile_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> PlayerView:
    profile = await get_or_create_profile(session, user.id)
    play = await get_play(session, user.id, conn.GAME_KEY, date.today())
    return to_player_view(profile, played_today=play is not None)


@router.get("/transactions", response_model=list[CoinTxnView])
async def list_transactions_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> list[CoinTxnView]:
    txns = await list_recent_txns(session, user.id)
    return [to_txn_view(txn) for txn in txns]


@router.get("/redemptions", response_model=list[RedemptionView])
async def list_redemptions_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> list[RedemptionView]:
    rows = sorted(
        await list_redemptions(session, user.id), key=lambda r: r.created_at, reverse=True
    )
    views: list[RedemptionView] = []
    for row in rows:
        reward = merch.get_reward(row.item_key)
        views.append(
            RedemptionView(
                item_key=row.item_key,
                title=reward.title if reward else row.item_key,
                emoji=reward.emoji if reward else "🎁",
                coins_spent=row.coins_spent,
                shipping_address=row.shipping_address,
                created_at=row.created_at,
            )
        )
    return views


@router.get("/connections", response_model=ConnectionsView)
async def get_connections_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> ConnectionsView:
    today = date.today()
    puzzle = conn.puzzle_for_date(today)
    play = await get_play(session, user.id, conn.GAME_KEY, today)
    return ConnectionsView(
        play_date=today,
        tiles=conn.daily_tiles(puzzle, today),
        group_count=len(puzzle.groups),
        group_size=len(puzzle.groups[0].members),
        difficulty=puzzle.difficulty,
        difficulty_label=conn.difficulty_label(puzzle),
        played=play is not None,
        solved=play.solved if play else False,
        score=play.score if play else 0,
    )


@router.post("/connections/attempt", response_model=ConnectionsResult)
async def attempt_connections_route(
    body: ConnectionsAttemptRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> ConnectionsResult:
    today = date.today()
    if await get_play(session, user.id, conn.GAME_KEY, today) is not None:
        raise ConflictError("You've already played today's Connections", code="already_played")
    if len(body.groups) != 4:
        raise ValidationError("Submit exactly four groups", code="invalid_groups")

    puzzle = conn.puzzle_for_date(today)
    correct = conn.grade(puzzle, body.groups)
    solved = correct == len(puzzle.groups)
    duration = max(0, body.duration_seconds)
    coins = CONNECTIONS_REWARD if solved else 0  # win → 10, otherwise → 0

    profile = await get_or_create_profile(session, user.id)
    bump_streak(profile, today)  # streak advances on playing (no coin payout)
    if coins:
        await award_coins(session, user_id=user.id, amount=coins, reason="connections")
    await add_play(
        session,
        user_id=user.id,
        game_key=conn.GAME_KEY,
        day=today,
        solved=solved,
        score=correct,
        duration_seconds=duration,
        coins_awarded=coins,
    )
    return ConnectionsResult(
        solved=solved,
        correct_groups=correct,
        total_groups=len(puzzle.groups),
        coins_awarded=coins,
        current_streak=profile.current_streak,
        new_balance=profile.coins,
        groups=[
            ConnGroupView(label=g.label, level=g.level, members=list(g.members))
            for g in puzzle.groups
        ],
    )


async def _all_time_board(session: AsyncSession, user: User) -> LeaderboardView:
    rows = await leaderboard_top(session, limit=20)
    top: list[LeaderboardEntry] = []
    me: LeaderboardEntry | None = None
    for index, (profile, owner) in enumerate(rows):
        entry = LeaderboardEntry(
            rank=index + 1,
            name=_display_name(owner),
            avatar_url=owner.avatar_url,
            is_me=owner.id == user.id,
            coins=profile.lifetime_coins,
        )
        top.append(entry)
        if entry.is_me:
            me = entry
    if me is None:
        profile = await get_or_create_profile(session, user.id)
        me = LeaderboardEntry(
            rank=await player_rank(session, profile.lifetime_coins),
            name=_display_name(user),
            avatar_url=user.avatar_url,
            is_me=True,
            coins=profile.lifetime_coins,
        )
    return LeaderboardView(period="all", top=top, me=me)


def _daily_entry(play: GamePlay, owner: User, rank: int, *, is_me: bool) -> LeaderboardEntry:
    return LeaderboardEntry(
        rank=rank,
        name=_display_name(owner),
        avatar_url=owner.avatar_url,
        is_me=is_me,
        coins=play.coins_awarded,
        correct=play.score,
        duration_seconds=play.duration_seconds,
    )


async def _today_board(session: AsyncSession, user: User) -> LeaderboardView:
    today = date.today()
    rows = await daily_leaderboard(session, conn.GAME_KEY, today, limit=20)
    top: list[LeaderboardEntry] = []
    me: LeaderboardEntry | None = None
    for index, (play, owner) in enumerate(rows):
        entry = _daily_entry(play, owner, index + 1, is_me=owner.id == user.id)
        top.append(entry)
        if entry.is_me:
            me = entry
    if me is None:
        my_play = await get_play(session, user.id, conn.GAME_KEY, today)
        if my_play is not None:
            rank = await daily_play_rank(
                session, conn.GAME_KEY, today, my_play.score, my_play.duration_seconds
            )
            me = _daily_entry(my_play, user, rank, is_me=True)
    return LeaderboardView(period="today", top=top, me=me)


@router.get("/leaderboard", response_model=LeaderboardView)
async def get_leaderboard_route(
    period: str = Query("all"),
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> LeaderboardView:
    if period == "today":
        return await _today_board(session, user)
    return await _all_time_board(session, user)


@router.post("/visit", response_model=DailyBonusView)
async def daily_visit_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> DailyBonusView:
    awarded = await daily_visit_bonus(session, user.id, date.today())
    profile = await get_or_create_profile(session, user.id)
    return DailyBonusView(awarded=awarded, coins=profile.coins)


@router.get("/rewards", response_model=RewardsView)
async def list_rewards_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> RewardsView:
    profile = await get_or_create_profile(session, user.id)
    claimed = {r.item_key for r in await list_redemptions(session, user.id)}
    return RewardsView(
        coins=profile.coins,
        rewards=[
            RewardView(
                key=r.key,
                title=r.title,
                emoji=r.emoji,
                cost=r.cost,
                claimed=r.key in claimed,
                affordable=profile.coins >= r.cost,
            )
            for r in merch.REWARDS
        ],
    )


@router.post("/rewards/{item_key}/redeem", response_model=PlayerView)
async def redeem_reward_route(
    item_key: str,
    body: RedeemRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> PlayerView:
    reward = merch.get_reward(item_key)
    if reward is None:
        raise NotFoundError("Reward not found", code="reward_not_found")
    if len(body.address.strip()) < 10:
        raise ValidationError("A full shipping address is required", code="address_required")
    claimed = {r.item_key for r in await list_redemptions(session, user.id)}
    if item_key in claimed:
        raise ConflictError("You've already redeemed this reward", code="reward_claimed")
    profile = await redeem_reward(
        session, user_id=user.id, item_key=item_key, cost=reward.cost, address=body.address.strip()
    )
    played = await get_play(session, user.id, conn.GAME_KEY, date.today())
    return to_player_view(profile, played_today=played is not None)


@router.post("/settle-daily", response_model=DailySettleView)
async def settle_daily_route(
    target: str | None = Query(None, alias="date"),
    x_settle_secret: str | None = Header(None),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(db_session),
) -> DailySettleView:
    """Award the nightly leaderboard bonus. Called by a scheduled job (cron).

    Guarded by a shared secret instead of a user session. With no ?date, it
    settles the day that just ended (yesterday in the server's timezone), which
    is what the midnight cron wants.
    """
    if not settings.settle_secret:
        raise DependencyUnavailableError(
            "Leaderboard settlement is not configured", code="settle_unavailable"
        )
    if not secrets.compare_digest(x_settle_secret or "", settings.settle_secret):
        raise PermissionDeniedError("Invalid settlement secret", code="bad_settle_secret")

    day = date.fromisoformat(target) if target else date.today() - timedelta(days=1)
    awarded = await settle_daily_leaderboard(session, game_key=conn.GAME_KEY, day=day)
    return DailySettleView(
        day=day,
        awards=[DailySettleAward(rank=rank, coins=coins) for _, rank, coins in awarded],
    )


@router.post("/course-slot", response_model=PlayerView)
async def buy_course_slot_route(
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> PlayerView:
    profile = await buy_course_slot(session, user_id=user.id, cost=EXTRA_COURSE_COST)
    played = await get_play(session, user.id, conn.GAME_KEY, date.today())
    return to_player_view(profile, played_today=played is not None)
