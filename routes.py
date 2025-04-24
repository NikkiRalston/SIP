import json
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from app import app, db
from model import User, JournalEntry  # fixed import from model.py


# if you have 3 neg emotions than you will get alerted
def detect_burnout(user_id):
    """
    Detect potential burnout based on negative mood patterns
    Simply counts the number of negative emotions and alerts after 3,
    unless positive emotions outnumber the negative ones.
    """
    # get recent entries (no time limit)
    recent_entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).all()
    # if no entries than nothing is detected
    if not recent_entries:
        return 0 
    
    # defining said negative moods
    negative_moods = ['Stressed', 'Anxious', 'Sad']
    # Defining positive moods to balance out negative ones
    positive_moods = ['Happy', 'Calm']
    
    # this counts the negative emotions for the burnout
    negative_count = sum(1 for entry in recent_entries if entry.mood in negative_moods)
    positive_count = sum(1 for entry in recent_entries if entry.mood in positive_moods)
    
    # simple scoring: 0 if less than 3 negative entries, or if positives outnumber negatives
    if negative_count >= 3 and positive_count <= negative_count:
        return 100
    else:
        return 0


# routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # it will tell you if your email/user already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        if email_exists:
            flash('Email already registered. Please use a different email.')
            return redirect(url_for('register'))
        
        # Creating new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        # will flash saing your user was successful in making
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # validating user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        # if you were in the journal before, you get a welcome back message
        login_user(user, remember=False)
        session.permanent = False
        flash(f'Welcome back, {username}!')
        
        # redirecting to next page or journal
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('journal')
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        mood = request.form.get('mood')
        entry = request.form.get('entry')
        
        # if you try to submit with no entry then it wont take it and tell you to enter something
        if not mood or not entry:
            flash('Please select a mood and write an entry.')
            return redirect(url_for('journal'))
        
        # Creating journal entry
        journal_entry = JournalEntry(
            mood=mood,
            content=entry,
            user_id=current_user.id
        )
        
        db.session.add(journal_entry)
        db.session.commit()
        
        flash('Your journal entry has been saved!')
        return redirect(url_for('journal'))
    
    # getting user's journal entries for display and mood tracking
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at.desc()).all()
    
    # getting burnout score
    burnout_score = detect_burnout(current_user.id)
    burnout_message = ""

    if burnout_score == 100:  # only showing message after 3 negative emotions
        burnout_message = (
            'You\'ve had 3 or more entries with negative emotions. '
            'Please take time to rest and consider talking to someone if you need support. Here are some <a href="/resources">resources</a>. '
        )

    #once things are submitted than you get a fresh journal ready for next entry but the burn out message stays until otherwise
    return render_template(
        'journal.html', 
        entries=entries, 
        burnout_score=burnout_score,
        burnout_message=burnout_message
    )



@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    # finding the entry to delete
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # ensuring the current user owns this entry
    if entry.user_id != current_user.id:
        flash('You do not have permission to delete this entry.')
        return redirect(url_for('journal'))
    
    # deleting the entry
    db.session.delete(entry)
    db.session.commit()
    #flash message saying its successful
    flash('Journal entry deleted successfully.')
    return redirect(url_for('journal'))

@app.route('/api/journal_entries')
@login_required
def get_journal_entries():
    """API endpoint to get journal entries for charts"""
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at).all()
    
    # forming data for scatter graph
    scatter_data = []
    for idx, entry in enumerate(entries):
        # the values of each emotion 0-5.
        mood_values = {
            'Happy': 5, 
            'Calm': 4, 
            'Neutral': 3, 
            'Anxious': 2, 
            'Stressed': 1, 
            'Sad': 0
        }
        
        # using the index as x-axis and mood value as y-axis
        scatter_data.append({
            'x': int(datetime(entry.created_at.year, entry.created_at.month, entry.created_at.day).replace(tzinfo=None).timestamp() * 1000),
            'y': mood_values.get(entry.mood, 3),  # default to neutral if unknown mood
            'mood': entry.mood,
            'date': entry.created_at.strftime('%B %d, %Y'), # Full month, day, year - no time
            'entry_preview': entry.content[:30] + '...' if len(entry.content) > 30 else entry.content
        })
    
    return jsonify(scatter_data)

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # a thank you message for using and submitting a contact
        flash('Thank you for your message! We will get back to you soon.')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')
