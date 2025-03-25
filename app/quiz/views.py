from marshmallow import ValidationError
from app.quiz.models import Answer
from app.quiz.schemes import AnswerSchema, QuestionSchema, ThemeSchema
from app.web.app import View
from app.web.utils import error_json_response, json_response
from aiohttp.web_exceptions import HTTPConflict,HTTPBadRequest,HTTPNotFound


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    async def post(self):
        try:
            data = ThemeSchema().load(data=await self.request.json())
        except ValidationError as e:
            return error_json_response(http_status=400,status="bad_request",message="Unprocessable Entity",data={"json":e.messages})
        title=data["title"]
        # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        theme = await self.store.quizzes.get_theme_by_title(title=title)
        if theme:
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    async def get(self):
        themes=await self.store.quizzes.list_themes()
        return json_response({"themes":[{"id":theme.id,"title":theme.title} for theme in themes]})


class QuestionAddView(View):
    async def post(self):
        try:
            data=QuestionSchema().load(await self.request.json())
        except ValidationError as e:
            return error_json_response(http_status=400,status="bad_request",message="Unprocessable Entity",data={"json":e.messages})
        
        answers=[Answer(ans["title"],ans["is_correct"]) for ans in data["answers"]]
        ok=False
        for ans in answers:
            if ans.is_correct:
                if not ok:
                    ok=True
                else:
                    raise HTTPBadRequest

        if not ok:
            raise HTTPBadRequest

        if len(answers)<=1:
            raise HTTPBadRequest
        
        theme=await self.store.quizzes.get_theme_by_id(data["theme_id"])
        if not theme:
            raise HTTPNotFound

        question=await self.store.quizzes.get_question_by_title(data["title"])
        if question:
            raise HTTPConflict
        
        q=await self.store.quizzes.create_question(data["title"],data["theme_id"],answers=answers)
        return json_response(
            data={
                "id":q.id,
                "title":q.title,
                "theme_id":q.theme_id,
                "answers":[{"title":ans.title, "is_correct":ans.is_correct} for ans in q.answers]
                }
            )


class QuestionListView(View):
    async def get(self):
        theme_id=self.request.query.get("theme_id")
        qs=await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(data={"questions":[QuestionSchema().dump(obj=q) for q in qs]})
        
