#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#
# Imports

import json
import dateutil.parser
import babel
from flask import (
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify
)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import sys
from models import app, db, Shows, Venue, Artist

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    #
    # replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venues = Venue.query.all()
    places = Venue.query.distinct(Venue.city, Venue.state).all()
    for place in places:
        data.append({
            "city": place.city,
            "state": place.state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    db.session.query(Shows)
                    .filter(
                        Shows.venue_id == venue.id,
                        Shows.start_time > datetime.now())
                    .all())
            } for venue in venues if venue.city == place.city and venue.state == place.state]
        })

    return render_template('pages/venues.html', areas=data)

#  Venues Search
#  ----------------------------------------------------------------


@app.route('/venues/search', methods=['POST'])
def search_venues():
    #
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    responses = Venue.query\
        .filter(
            Venue.name.ilike('%'+search_term+'%')
        )\
        .order_by('id')\
        .all()
    response = {
        'count': len(responses),
        'data': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(
                Shows.query
                .filter(
                    Shows.venue_id == venue.id,
                    Shows.start_time > datetime.now()
                )
                .all()
            )
        } for venue in responses]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


#  Show Venue
#  ----------------------------------------------------------------

@app.route('/venue/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    #
    # replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get_or_404(venue_id)

    past_shows = db.session.query(Artist, Shows).join(Shows).filter(
        Shows.venue_id == venue_id,
        Shows.start_time < datetime.now()
    ).all()

    upcoming_shows = db.session.query(Artist, Shows).join(Shows).filter(
        Shows.venue_id == venue_id,
        Shows.start_time > datetime.now()
    ).all()

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")} for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")} for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = Venue()
            form.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + form.name.data + ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('An error occurred. Venue ' +
                  form.name + ' could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join.err)
        flash('Errors' + str(message))

    return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------


@ app.route('/venue/<int:venue_id>/delete', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
    #
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    venue = Venue.query.get_or_404(venue_id)
    shows = Shows.query.filter_by(venue_id=venue_id).all()
    try:
        db.session.delete(venue)
        for show in shows:
            db.session.delete(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    if not error:
        flash('Venue: ' + venue.name + ' has been deleted.')
    else:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
    return render_template('pages/home.html')

#  Edit Venue
#  ----------------------------------------------------------------


@ app.route('/venue/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    #
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = db.session.query(Venue).get_or_404(venue_id)
            form.populate_obj(venue)
            db.session.commit()

        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()

        if not error:
            flash('Venue: ' + form.name.data + ' updates have been saved.')
        else:
            flash('An error occurred. Venue ' +
                  form.name.data + ' could not be updated. Please try again later.')

        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors' + str(message))
        return render_template('pages/home.html')


@ app.route('/venue/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)
        form = VenueForm(obj=venue)
    # populate form with values from venue with ID <venue_id>
    except:
        flash('Venue id: ' + venue_id + ' doesnt exist.')
        return render_template('templates/pages/home.html')

    return render_template('forms/edit_venue.html', form=form, venue=venue)


#  Artists
#  ----------------------------------------------------------------

@ app.route('/artists')
def artists():
    #
    # replace with real data returned from querying the database
    artists = Artist.query.order_by('id').all()
    data = [{
        "id": artist.id,
        "name": artist.name
    } for artist in artists]
    return render_template('pages/artists.html', artists=data)

#  Artists Search
#  ----------------------------------------------------------------


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    #
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    responses = Artist.query\
        .filter(
            Artist.name.ilike('%'+search_term+'%')
        )\
        .order_by('id')\
        .all()
    response = {
        'count': len(responses),
        'data': [{
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(
                Shows.query
                .filter(
                    Shows.artist_id == artist.id,
                    Shows.start_time > datetime.now()
                )
                .all())
        } for artist in responses]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Show Artist
#  ----------------------------------------------------------------


@ app.route('/artist/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    #
    # replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get_or_404(artist_id)

    past_shows = db.session.query(Venue, Shows).join(Shows)\
        .filter(
        Shows.artist_id == artist_id,
        Shows.start_time < datetime.now()
    )\
        .all()

    upcoming_shows = db.session.query(Venue, Shows).join(Shows)\
        .filter(
        Shows.artist_id == artist_id,
        Shows.start_time > datetime.now()
    )\
        .all()

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'address': artist.address,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")} for venue, show in past_shows],
        'upcoming_shows': [{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")} for venue, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artist/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artist/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    #
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            artist = Artist.query.get_or_404(artist_id)
            form.populate_obj(artist)
            db.session.commit()

        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()

        if not error:
            flash('Artist: ' + form.name.data + ' updates have been saved.')
        else:
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be updated. Please try again later.')
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors' + str(message))
        return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------


@ app.route('/artist/<int:artist_id>/delete', methods=['GET', 'DELETE'])
def delete_artist(artist_id):
    #
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    artist = Artist.query.get_or_404(artist_id)
    shows = Shows.query.filter_by(artist_id=artist_id).all()
    name = artist.name
    try:
        db.session.delete(artist)
        for show in shows:
            db.session.delete(show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Artist on a Artist Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    if not error:
        flash('Artist: ' + name + ' has been deleted.')
    else:
        flash('An error occurred. Venue ' +
              name + ' could not be deleted.')
    return render_template('pages/home.html')


#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    #
    # insert form data as a new Artist record in the db, instead
    #
    # modify data to be the data object returned from db insertion
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            artist = Artist()
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + form.name.data + ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('An error occurred. Artist ' +
                  name + ' could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors' + str(message))

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    #
    # replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows_details = db.session.query(
        Venue, Artist, Shows).join(Venue).join(Artist)

    data = [{
        "venue_id": show_details.Venue.id,
        "venue_name": show_details.Venue.name,
        "artist_id": show_details.Artist.id,
        "artist_name": show_details.Artist.name,
        "artist_image_link": show_details.Artist.image_link,
        "start_time": show_details.Shows.start_time.strftime("%Y-%m-%d, %H:%M:%S")
    } for show_details in shows_details]

    return render_template('pages/shows.html', shows=data)

#  Create Shows
#  ----------------------------------------------------------------


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowsForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead
    form = ShowsForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue_id = Venue.query.get(form.venue_id.data)
            artist_id = Artist.query.get(form.artist_id.data)
            if venue_id and artist_id:
                shows = Shows()
                form.populate_obj(shows)
                db.session.add(shows)
                db.session.commit()
                # on successful db insert, flash success
                flash('Show was successfully listed!')
            else:
                flash('Invalid artist or venue')
        except ValueError as e:
            # error = True
            print(e)
            db.session.rollback()
            #
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        finally:
            db.session.close()
        # if not error:
        # else:
    else:
        message = []
        for field, err in form.errors.items():
            message.append(err + ' ' + '|'.join(err))
        flash('Errors' + str(message))
    return render_template('pages/home.html')

#  Search Shows
#  ----------------------------------------------------------------


@ app.route('/shows/search/artist_id', methods=['POST'])
def search_shows_artist():
    form = ShowByArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            search_term = form.artist_search_term.data
            responses = db.session.query(Artist, Shows, Venue)\
                .filter(
                Shows.artist_id == search_term,
                Venue.id == Shows.venue_id,
                Artist.id == search_term
            )\
                .all()
            if len(responses) == 0:
                flash('No shows for the artist')
            response = {
                'count': len(responses),
                'data': [{
                    'venue_id': venue.id,
                    'venue_name': venue.name,
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'num_upcoming_shows': len(db.session.query(Shows)
                                              .filter(
                        Shows.venue_id == venue.id,
                        Shows.start_time > datetime.now()
                    ).all())
                } for artist, show, venue in responses]
            }
            return render_template('pages/show.html', results=response, search_term=form.artist_search_term.data)
        except ValueError as e:
            print(e)
    else:
        print(form.artist_search_term.data)
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Enter a valid id')
        return render_template('errors/404.html')


@ app.route('/shows/search/venue_id', methods=['POST'])
def search_shows_venue():
    form = ShowByVenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            search_term = form.venue_search_term.data
            responses = db.session.query(Artist, Shows, Venue).filter(
                Shows.venue_id == search_term,
                Artist.id == Shows.artist_id,
                Venue.id == search_term
            ).all()
            response = {
                'count': len(responses),
                'data': [{
                    'venue_id': venue.id,
                    'venue_name': venue.name,
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'num_upcoming_shows': len(db.session.query(Shows)
                                              .filter(
                        Shows.venue_id == venue.id,
                        Shows.start_time > datetime.now()
                    ).all())
                } for artist, show, venue in responses]
            }
            return render_template('pages/show.html', results=response, search_term=form.venue_search_term.data)
        except ValueError as e:
            print(e)
    else:
        print(form.venue_search_term.data)
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash(field + ' ' + '|'.join(err))
        return render_template('errors/404.html')

#----------------------------------------------------------------------------#
# Errors.
#----------------------------------------------------------------------------#


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
