import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Question Z?',
            'answer': 'Answer for this question',
            'category': '5',
            'difficulty': 4,
        }

        self.question_404 = {
            'question': '',
            'answer': '',
            'category': '5',
            'difficulty': 4,
        }

        self.unprocessable = {
            'question': 'Question Z?',
            'answer': 'Answer for this question',
            'category': '5',
            'difficulty': "'4'",
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_success_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['categories'])

    def test_success_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_success_get_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_get_questions(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_success_delete_question(self):
        res = self.client().delete('/questions/17')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # def test_404_delete_question(self):
    #     res = self.client().delete('/questions/1000')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)
    #     self.assertTrue(data['message'])

    def test_success_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # def test_404_add_question(self):
    #     res = self.client().post('/questions', json=self.question_404)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)
    #     self.assertTrue(data['message'])

    def test_422_add_question(self):
        res = self.client().post('/questions', json=self.unprocessable)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_success_search_question(self):
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "Title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_search_question(self):
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "xyz"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_422_search_question(self):
        res = self.client().post('/questions/search', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_200_get_questions_bycategory(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_question_by_catgory(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_200_get_quiz_questions(self):
        res = self.client().post('/quizzes',
                                 json={"previous_questions": [5, 9], "quiz_category": {"type": "click", "id": 4}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_400_get_quiz_questions_missing_questions(self):
        res = self.client().post(
            '/quizzes', json={"quiz_category": {"type": "click", "id": 0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_400_get_quiz_questions_missing_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
