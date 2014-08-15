inquire
=======

Inquire is a simple factoid question answering system written in Python. You ask a question and
Inquire will try to answer it. This is still a work in progress, and the system currently only knows
how to answer a few types of questions. You can see a demo of it running
[here](http://inquire.exathread.com). Currently the system performs best with questions about people
and places (e.g., "Who was the third Prime Minister of Canada?" or "What is the capital of
Bangladesh?").

Inquire consists of three main components:

* **Classification**: attempts to classify the question as one of 50 classes. This information is
  used to determine which answer extractor module to use. In the future it will also be used to
  choose different document retrieval strategies.
* **Retrieval**: gets documents from the internet that may contain the answer to our question.
  Currently this is using the Bing web search API, but in the future it will also have the ability
  to get data from more structured sources (e.g., DBPedia).
* **Extraction**: implements strategies for getting answers out of candidate documents. This package
  dynamically loads the appropriate module based on the given question class. This is where the
  majority of the improvements can be made to the system.
