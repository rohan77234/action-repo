from flask import Blueprint, request, jsonify, render_template
from app import mongo
from datetime import datetime
import re

bp = Blueprint('webhook', __name__)


@bp.route('/')
def dashboard():
    return render_template('index.html')  # Fixed path


@bp.route('/webhook', methods=['POST'])
def handle_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event_type == 'push':
        process_push_event(payload)
    elif event_type == 'pull_request':
        process_pull_request_event(payload)

    return jsonify(status='received'), 200


@bp.route('/events')
def get_events():
    events = mongo.db.events
    recent_events = list(events.find().sort('timestamp', -1).limit(50))
    return jsonify([format_event(e) for e in recent_events])


def process_push_event(payload):
    events = mongo.db.events
    events.insert_one({
        'author': payload['pusher']['name'],
        'action': 'PUSH',
        'to_branch': extract_branch_name(payload['ref']),
        'timestamp': datetime.utcnow(),
        'request_id': payload['head_commit']['id'][:7]
    })


def process_pull_request_event(payload):
    pr = payload['pull_request']
    action = payload['action']

    if action == 'closed' and pr.get('merged', False):
        event_type = 'MERGE'
    elif action in ['opened', 'reopened']:
        event_type = 'PULL_REQUEST'
    else:
        return

    events = mongo.db.events
    events.insert_one({
        'author': pr['user']['login'],
        'action': event_type,
        'from_branch': pr['head']['ref'],
        'to_branch': pr['base']['ref'],
        'timestamp': datetime.utcnow(),
        'request_id': str(pr['number'])
    })


def extract_branch_name(ref):
    # Extract branch name from ref string (refs/heads/main)
    return ref.split('/')[-1] if ref.startswith('refs/heads/') else ref


def format_event(event):
    timestamp = format_datetime(event['timestamp'])

    if event['action'] == 'PUSH':
        return f"{event['author']} pushed to {event['to_branch']} on {timestamp}"
    elif event['action'] == 'PULL_REQUEST':
        return f"{event['author']} submitted a pull request from {event['from_branch']} to {event['to_branch']} on {timestamp}"
    elif event['action'] == 'MERGE':
        return f"{event['author']} merged branch {event['from_branch']} to {event['to_branch']} on {timestamp}"


def format_datetime(dt):
    day = dt.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return dt.strftime(f"%d{suffix} %B %Y - %I:%M %p UTC")