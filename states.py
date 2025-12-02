from aiogram.fsm.state import StatesGroup, State


class CareerState(StatesGroup):
    waiting_for_input = State()


class ResumeCreateState(StatesGroup):
    waiting_for_input = State()


class ResumeCheckState(StatesGroup):
    waiting_for_resume = State()


class MockInterviewState(StatesGroup):
    waiting_for_dialog = State()


class InterviewPlanState(StatesGroup):
    waiting_for_info = State()


class SoftSkillsState(StatesGroup):
    waiting_for_answers = State()


class VacancyMatchState(StatesGroup):
    waiting_for_vacancy = State()
    waiting_for_profile = State()


class CoursesState(StatesGroup):
    waiting_for_info = State()
