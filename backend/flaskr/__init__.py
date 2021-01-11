import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    try:
      categories=Category.query.all()
      return jsonify({
        'success':True,
        'categories':{category.id: category.type for category in categories}
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    questions= Question.query.all()
    print(questions)
    questions_formatted=[question.format() for question in questions]
    print(questions_formatted)
    page= request.args.get('page', 1, type= int)
    start= (page-1)*10
    end= start+10
    categories=Category.query.all()
    if len(questions_formatted[start:end]) is 0 :
      abort(404)
    return jsonify({
      'success':True,
      'questions':questions_formatted[start:end],
      'total_questions':len(questions_formatted),
      'categories':{category.id: category.type for category in categories}
    })
    
      
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      questions=Question.query.all()
      print(questions)
      question= Question.query.get(question_id)
      print(question)
      question.delete()
      print('deleted')
      return jsonify({
        'success':True,
        'message':'The question is deleted successively',
        'deleted':question_id,
        'total_questions':len([question.format() for question in questions])
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_questions(): 
    try:
      print('add_question')
      question_text = request.get_json()['question']
      print(question_text)
      answer_text = request.get_json()['answer']
      category = request.get_json()['category']
      difficulty_score = request.get_json()['difficulty']
      print(difficulty_score)
      
      new_question=Question(question=question_text, answer=answer_text, category=category, difficulty=difficulty_score)
      new_question.insert()
      print(new_question.id,'added')
     
      return jsonify({
        'success':True,
        'message':'The question is created'
  
      })
    except:
      print(sys.exc_info())
      abort(422)
      
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question(): 
    print('searching')
    search_term =request.get_json()['searchTerm']
    print(search_term)
    questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    questions_formatted= [question.format() for question in questions]
    if len(questions_formatted) is 0:
      abort(404)
    return jsonify({
        'success':True,
        'search_term':search_term,
        'questions': questions_formatted
      })
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    try:
      questions= Question.query.filter(Question.category==category_id).all()
      print(questions)
      questions_formatted=[question.format() for question in questions]
      print(questions_formatted)
      category= Category.query.get(category_id)
      category_type= category.type
      page= request.args.get('page', 1, type= int)
      start= (page-1)*10
      end= start+10
      return jsonify({
        'success':True,
        'questions':questions_formatted[start:end],
        'current_category': category_type,
        'total_questions':len(questions_formatted)
      })
    except:
      abort(404)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quiz/questions', methods=['POST'])
  def quiz_questions(): 
    try:
      category = request.get_json()['quiz_category']
      print(category)
      if category['id'] is 0:
        print('all')
        questions=Question.query.all()
        questions_formatted= [question.format() for question in questions]
      else:
        print(category['type'],category['id'])
        questions=Question.query.filter(Question.category==category['id']).all()
        questions_formatted= [question.format() for question in questions]
        print(questions_formatted)
      print(len(questions_formatted))
      if len(questions_formatted)>5:
        quiz_questions= random.sample(questions_formatted,5)
        print(quiz_questions)
      else:
        quiz_questions=questions_formatted
        print(quiz_questions)
      
      previous_questions= request.get_json()['previous_questions']
      print(len(quiz_questions))
      if len(quiz_questions) is 1:
        quiz_question=quiz_questions
      else:
        question= random.sample(quiz_questions,1)
        print(question)
        if question in previous_questions:
          quiz_questions.remove(question)
          print('remove previous question')
          quiz_question= random.sample(quiz_questions,1)
        else:
          print('return')
          quiz_question= question
      return jsonify({
        'success':True,
        'question': quiz_question[0]
      })
    except:
      print(sys.exc_info())
      abort(404)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

  return app

    