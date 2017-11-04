# -*- coding: utf-8 -*-
# Calculates history of KSP levels.
# Supports updates with finished semester or camp.

from collections import namedtuple, defaultdict

from django.db.models import Q

from trojsten.contests.models import Round, Competition
from trojsten.events.models import Event, EventParticipant
from trojsten.results.manager import get_results
from trojsten.rules.models import KSPLevel


# Either a semester or a camp which will yield level-ups.
ResultsAffectingEvent = namedtuple('ResultsAffectingEvent',
                                   'start_time, semester, camp, associated_semester, last_semester_before_level_up')


def prepare_events(latest_event_start_date):
    """Produces a list of all ResultsAffectingEvents sorted by their start dates."""
    last_rounds = Round.objects.filter(
        semester__competition__name='KSP', start_time__lte=latest_event_start_date
    ).order_by(
        'semester', 'start_time', 'pk'
    ).distinct(
        'semester'
    ).select_related('semester')

    semesters = []
    for last_round in last_rounds:
        semesters.append(ResultsAffectingEvent(
            start_time=last_round.start_time,
            semester=last_round.semester,
            camp=None,
            associated_semester=last_round.semester,
            last_semester_before_level_up=last_round.semester
        ))

    ksp_site_id = Competition.objects.get(name='KSP').sites.first().id
    camp_objects = Event.objects.filter(
        type__is_camp=True, start_time__lte=latest_event_start_date
    ).filter(
        type__sites__in=[ksp_site_id]
    ).order_by('start_time').select_related('semester')

    camps = []
    for camp_object in camp_objects:
        camps.append(ResultsAffectingEvent(
            start_time=camp_object.start_time,
            semester=None,
            camp=camp_object,
            associated_semester=camp_object.semester,
            last_semester_before_level_up=None
        ))

    events = sorted(semesters + camps)

    # Find last semester before level up for each camp.
    for i in range(len(events)):
        if events[i].camp is not None:
            # If camp is at i-th position, at (i-1)-th position should be the current semester.
            if i - 1 >= 0 and events[i - 1].semester is not None:
                events[i] = events[i]._replace(
                    last_semester_before_level_up=events[i - 1].semester,
                )

    return events


def level_updates_from_semester_results(semester, level_up_score_limits_for_table_levels=None):
    """
    Returns a list of LevelUpRecords for users whose level should be updated.
    First 5 competitors from each level get a levelling boost (results_table_level + 1) for the next semester.
    """
    if level_up_score_limits_for_table_levels is None:
        level_up_score_limits_for_table_levels = defaultdict(lambda: 150)

    round = Round.objects.filter(semester=semester).order_by('number').last()
    # TODO: Get frozen results table if available.
    result_tables = [(get_results('KSP_L{}'.format(level), round, single_round=False), level) for level in range(1, 4)]

    updates = []
    for table, table_level in result_tables:
        for row in table.rows:
            if not row.active:
                continue
            if int(row.rank) > 5 or float(row.total) < level_up_score_limits_for_table_levels[table_level]:
                break
            level_up = KSPLevel(
                user=row.user,
                new_level=min(4, table_level + 1),
                source_semester=semester,
                last_semester_before_level_up=semester
            )
            updates.append(level_up)

    return updates


def level_updates_from_camp_attendance(camp, associated_semester, last_semester_before_level_up,
                                       level_up_score_limits_for_user_levels=None):
    """
    Returns a list of LevelUpRecords for users whose level should be updated.
    All participants who were invited for their success in KSP (reached at least 100 points)
    will receive a levelling boost (associated_semester_competitor_level + 1) for the next semester.
    """
    if level_up_score_limits_for_user_levels is None:
        level_up_score_limits_for_user_levels = defaultdict(lambda: 100)

    invited_users_pks = EventParticipant.objects.filter(
        Q(type=EventParticipant.PARTICIPANT) | Q(type=EventParticipant.RESERVE),
        event=camp,
        going=True,
    ).values_list('user__pk', flat=True)
    invited_users_pks_set = set(invited_users_pks)

    user_levels = KSPLevel.objects.for_users_in_semester_as_dict(associated_semester.pk, invited_users_pks)

    last_round = Round.objects.filter(semester=associated_semester).order_by('number').last()

    # TODO: Get frozen results table if available.
    results_table = get_results('KSP_ALL', last_round, single_round=False)

    updates = []
    for row in results_table.rows:
        if row.user.pk not in invited_users_pks_set:
            continue
        if float(row.total) < level_up_score_limits_for_user_levels[user_levels[row.user.pk]]:
            break
        level_up = KSPLevel(
            user=row.user,
            new_level=min(4, user_levels[row.user.pk] + 1),
            source_camp=camp,
            last_semester_before_level_up=last_semester_before_level_up
        )
        updates.append(level_up)

    return updates