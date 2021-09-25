#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from werkzeug.wrappers import response
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy.orm import lazyload
from sqlalchemy import create_engine
from sqlalchemy.sql import text 
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db) 
#// TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///fyyur'
engine = create_engine('postgresql:///fyyur')

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#^ (Optional) TODO: Location relationship

#*Completed*
artist_genres = db.Table("artist_genres", 
                          db.Column("genre_id",db.Integer, db.ForeignKey('genres.id'), nullable = False, primary_key = True),
                          db.Column("artist_id",db.Integer, db.ForeignKey('artists.id'), nullable = False, primary_key = True)
                          )

#*Completed*
venue_genres = db.Table("venue_genres", 
                          db.Column("genre_id",db.Integer, db.ForeignKey('genres.id'), nullable = False, primary_key = True),
                          db.Column("venue_id",db.Integer, db.ForeignKey('venues.id'), nullable = False, primary_key = True)
                          )

# *Completed* 
class Venues(db.Model): 
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), default="")
    facebook_link = db.Column(db.String(500), default="")
    website_link = db.Column(db.String(500), default="")
    talent_hunting = db.Column(db.Boolean, nullable=False, default=False)
    talent_description = db.Column(db.String(500), nullable=False)
    genres = db.relationship('Genres', secondary= venue_genres, backref=db.backref('venue', lazy=True))
    # shows = db.relationship('shows_list', backref='show', lazy=True)

# *Completed* 
class Artists(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), default="")
    facebook_link = db.Column(db.String(120), default="")
    website_link = db.Column(db.String(120), default="")
    venue_hunting = db.Column(db.Boolean, nullable=False, default=False)
    venue_description = db.Column(db.String(500), nullable=False)
    genres = db.relationship('Genres', secondary= artist_genres, backref=db.backref('artist', lazy=True))
    # shows = db.relationship('shows_list', backref='show', lazy=True)

# *Completed*
class Genres(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    genres = db.Column(db.String(120), nullable=False)

# *Completed*
class ShowsList(db.Model):
    __tablename__ = 'shows_list'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable = False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable = False)
    event_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format="EEEE dd, MMMM, y 'at' h:mma"
    elif format == 'medium':
        format="EE dd, MM, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')        

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
# *Completed*
@app.route('/venues')
def venues():
  data = Venues.query.distinct(Venues.city).all()
  venues = Venues.query.all()
  return render_template('pages/venues.html', areas=data, venues=venues);

# *Completed*
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term=request.form.get('search_term', '')
    filtering = Venues.query.filter(Venues.name.ilike('%'+search_term+'%'))
    response = filtering.order_by('id').all()
    count = filtering.count()
    return render_template('pages/search_venues.html', results=response, search_term=search_term, count=count)

# *Completed*
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  now = datetime.now()
  data = db.session.query(ShowsList,Artists).join(Artists).filter(ShowsList.venue_id==venue_id)
  past_shows = data.filter(ShowsList.event_time<now)
  upcoming_shows = data.filter(ShowsList.event_time>=now)
  venue = Venues.query.get(venue_id)
  
  return render_template('pages/show_venue.html', 
                         venue=venue, 
                         past_shows_count = past_shows.count(), 
                         past_shows = past_shows.all(), 
                         upcoming_shows_count = upcoming_shows.count(), 
                         upcoming_shows = upcoming_shows.all())
  
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# *Completed*
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        address = request.get_json()['address']
        phone = request.get_json()['phone']
        genres = request.get_json()['genres']
        facebook_link = request.get_json()['facebook_link']
        image_link = request.get_json()['image_link']
        website_link = request.get_json()['website_link']
        seeking_talent = request.get_json()['seeking_talent']
        seeking_description = request.get_json()['seeking_description']
        venues = Venues(
                    name = name,
                    city  = city,
                    state  = state,
                    address  = address,
                    phone  = phone,
                    image_link  = image_link,
                    facebook_link  = facebook_link,
                    website_link  = website_link,
                    talent_hunting  = seeking_talent,
                    talent_description  = seeking_description
                    )
        db.session.add(venues)
        db.session.commit()
        for genre in genres:
              venue_genres = Genres.query.filter_by(genres=genre).first()
              venues.genres.append(venue_genres)
              db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + name + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        # return render_template('pages/home.html')
        return redirect(url_for('index'))


# *Completed*
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venues.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # return redirect(url_for('index'))
    return jsonify({'success': True})
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Artists
#  ----------------------------------------------------------------
# *Completed*
@app.route('/artists')
def artists():
    data = Artists.query.all()
    return render_template('pages/artists.html', artists=data)

# *Completed*
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term=request.form.get('search_term', '')
    filtering = Artists.query.filter(Artists.name.ilike('%'+search_term+'%'))
    response = filtering.order_by('id').all()
    count = filtering.count()

    return render_template('pages/search_artists.html', results=response, search_term=search_term, count=count)

# *Completed*
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artists.query.get(artist_id)
  now = datetime.now()
  data = db.session.query(ShowsList,Venues).join(Venues).filter(ShowsList.artist_id==artist_id)
  past_shows = data.filter(ShowsList.event_time<now)
  upcoming_shows = data.filter(ShowsList.event_time>=now)
  
  return render_template('pages/show_artist.html', 
                         artist=artist, 
                         past_shows_count = past_shows.count(), 
                         past_shows = past_shows.all(), 
                         upcoming_shows_count = upcoming_shows.count(), 
                         upcoming_shows = upcoming_shows.all())


#  Update
#  ----------------------------------------------------------------
# *Completed*
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artists.query.get(artist_id)
  genres = Genres.query.all()
  return render_template('forms/edit_artist.html', form=form, artist=artist, genres=genres)

# TODO
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

# *Completed*
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venues.query.get(venue_id)
  genres = Genres.query.all()
  return render_template('forms/edit_venue.html', form=form, venue=venue, genres=genres)

# TODO
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# *Completed*
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        phone = request.get_json()['phone']
        genres = request.get_json()['genres']
        facebook_link = request.get_json()['facebook_link']
        image_link = request.get_json()['image_link']
        website_link = request.get_json()['website_link']
        seeking_venue = request.get_json()['seeking_venue']
        seeking_description = request.get_json()['seeking_description']
        artists = Artists(
                        name = name,
                        city  = city,
                        state  = state,
                        phone  = phone,
                        image_link  = image_link,
                        facebook_link  = facebook_link,
                        website_link  = website_link,
                        venue_hunting  = seeking_venue,
                        venue_description  = seeking_description
                    )
        db.session.add(artists)
        db.session.commit()
        for genre in genres:
              artist_genres = Genres.query.filter_by(genres=genre).first()
              artists.genres.append(artist_genres)
              db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + name + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + name + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        # return render_template('pages/home.html')
        return redirect(url_for('index'))
    #   # on successful db insert, flash success
    #   flash('Artist ' + request.form['name'] + ' was successfully listed!')
    #   #  on unsuccessful db insert, flash an error instead.
    #   # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    #   return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

# *Completed*
@app.route('/shows')
def shows():
    data = db.session.query(ShowsList,Venues,Artists).select_from(ShowsList).join(Venues).join(Artists).all()
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# *Completed*
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        venue_id = request.get_json()['venue_id']
        artist_id = request.get_json()['artist_id']
        event_time = request.get_json()['start_time']
        show = ShowsList(
                    venue_id = venue_id,
                    artist_id  = artist_id,
                    event_time  = event_time,
                    )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('The show at ' + event_time + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. The show at ' + event_time + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# VM Box port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug = True)

