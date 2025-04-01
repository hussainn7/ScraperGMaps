from flask import Flask, render_template, request, jsonify, session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from scraper import RealEstateScraper
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
bootstrap = Bootstrap5(app)

class ScraperForm(FlaskForm):
    chromedriver_path = StringField('ChromeDriver Path', validators=[DataRequired()])
    chrome_path = StringField('Chrome Path', validators=[DataRequired()])
    max_companies = IntegerField('Maximum Companies', default=20)
    search_query = StringField('Search Query', validators=[DataRequired()], default='Plumbing in Nashville')
    submit = SubmitField('Start Scraping')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScraperForm()
    if form.validate_on_submit():
        try:
            scraper = RealEstateScraper(
                driver_path=form.chromedriver_path.data,
                chrome_path=form.chrome_path.data,
                max_companies=form.max_companies.data,
                search_query=form.search_query.data
            )
            results = scraper.run()
            return render_template('results.html', results=results)
        except Exception as e:
            return render_template('index.html', form=form, error=str(e))
    return render_template('index.html', form=form)

@app.route('/status')
def status():
    # You could implement real-time status updates here
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    app.run(debug=True)
