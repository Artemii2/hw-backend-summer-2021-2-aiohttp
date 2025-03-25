from marshmallow import Schema, fields

from app.quiz.models import Answer


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.List(fields.Nested(AnswerSchema),required=True)

class ThemeListSchema(Schema):
    pass


class ThemeIdSchema(Schema):
    pass


class ListQuestionSchema(Schema):
    pass
