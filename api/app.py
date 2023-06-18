from flask import Flask, Response, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def root():
    return 'test'

@app.route('/prove')
def prove():
    goal = request.args.get('goal')

    stream = [goal[:-i] for i in range(len(goal))]
    def event_stream():
        for event in stream:
            yield event
            time.sleep(1)

    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run()