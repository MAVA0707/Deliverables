GOAL:  create quizzes about a python file to check our understanding of the code and its internal organization. 

Input: a python program

Output: it should create a quiz that has a mix of low and high levels of depth and detail. The  combination are valid:

Low depth, low detail
Low depth, high detail
High depth, high detail
High depth low detail 


Steps:
LLM should understand the content of the file 
LLM should cover the key classes, structures, functions that inside of it
LLM should provide the user with the correct answer
Any time a question regarding an executable part of the code is created, the code should be run and executed first to ensure validity of the answer
If the code has a clear or obvious error, you are also allowed to give it to the user 
Linters should be used to create questions regarding code improvements


Design and execution:
Create a html quarto presentation with the question, code and a hidden answer in the following slide
Execution should be done via a python module, i.e. `python codecheck script.py -n quiz1` should generate a html of quiz1. If no name is given, a random unique identifier will be generated for that file. 


Tech Stack:
OpenAI
Quarto
Python 3.8+
Pytest
No vectorstores
