from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
# from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField
from wtforms.validators import Required

# import inquire
from inquire import inquire


class ExampleForm(Form):
    question = TextField('Question', description='', validators=[Required()])
    submit_button = SubmitField('Go')


def create_app(configfile=None):
    app = Flask(__name__)
    # AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

    @app.route('/', methods=('GET', 'POST'))
    def index():
        if request.method == 'POST':
            question = request.form['question']
            print(question)
            answer = inquire.answer_question(question)
            return render_template('answer.html', answer=answer)

        form = ExampleForm()
        return render_template('index.html', form=form)

    # @app.route('/answer')
    # def answer():
    #     form

    return app

if __name__ == '__main__':
    create_app().run(debug=True)

