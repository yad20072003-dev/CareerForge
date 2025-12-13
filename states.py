from aiogram.fsm.state import StatesGroup, State


class CareerState(StatesGroup):
    waiting_for_basic = State()
    waiting_for_education = State()
    waiting_for_experience = State()
    waiting_for_interests = State()
    waiting_for_preferences = State()
    waiting_for_goals = State()


class ResumeCreateState(StatesGroup):
    waiting_for_position = State()
    waiting_for_contacts = State()
    waiting_for_experience = State()
    waiting_for_education = State()
    waiting_for_skills = State()
    waiting_for_projects = State()
    waiting_for_extra = State()


class ResumeCheckState(StatesGroup):
    waiting_for_resume = State()


class MockInterviewState(StatesGroup):
    waiting_for_position = State()
    waiting_for_experience = State()
    waiting_for_goals = State()
    in_interview = State()


class MockClarifyState(StatesGroup):
    waiting_for_clarify = State()


class InterviewPlanState(StatesGroup):
    waiting_for_info = State()


class VacancyMatchState(StatesGroup):
    waiting_for_vacancy = State()
    waiting_for_profile = State()


class CompetitivenessState(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
