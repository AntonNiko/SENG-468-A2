from datetime import datetime
import time
import redis
from flask import Flask, send_from_directory, request

app = Flask(__name__)
cache = redis.StrictRedis(host='redis', port=6379)

CACHE_ORDERED_SET_NAME = 'orders'

@app.route('/')
def root():
    return send_from_directory('views', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('views', 'admin.html')

@app.route('/get_order_table')
def get_order_table():
    orders = cache.zrange(CACHE_ORDERED_SET_NAME, 0, -1, withscores=True)

    html_output = '<table>'
    html_output+= '<tr><th>Date Ordered</th><th>Username</th><th>Book Name</th><th>Quantity</th></tr>'

    # For each order, output in correct format.
    for order in orders:
        username, bookname, quantity = order[0].decode('utf-8').split(';')
        timestamp = order[1]
        utc_timestamp = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        html_output+= '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(utc_timestamp, username, bookname, quantity)
    html_output+='</table>'
    html_output+='<style>table, th, td { border: 1px solid black; }</style>'

    return html_output

@app.route('/submit_order', methods=['POST'])
def submit_order():
    username = request.form.get('username')
    bookname = request.form.get('bookname')
    quantity = request.form.get('quantity')

    # Get UNIX timestamp to store in cache
    timestamp = int(time.time())
    cache_value = '{};{};{}'.format(str(username), str(bookname), str(quantity))

    # Add to redis
    cache.zadd(CACHE_ORDERED_SET_NAME, {cache_value: timestamp})
    return {'success': 'true'}