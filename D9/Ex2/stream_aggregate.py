import faust

# Define the app
app = faust.App('sensor-avg-app', broker='kafka://localhost:9094')

# Define input and output topics
class SensorReading(faust.Record, serializer='json'):
    sensor_id: str
    value: float

class SensorAvg(faust.Record, serializer='json'):
    sensor_id: str
    avg: float

sensor_topic = app.topic('sensor-data', value_type=SensorReading)
avg_topic = app.topic('sensor-avg', value_type=SensorAvg, partitions=1)

# Table to keep track of running totals and counts
sensor_totals = app.Table('sensor_totals', default=lambda: {'sum': 0.0, 'count': 0}, partitions=1)

# compute the average for each sensor_id
@app.agent(sensor_topic)
async def compute_average(stream):
    async for event in stream:
        totals = sensor_totals[event.sensor_id]
        print(totals)
        totals['sum'] += event.value
        totals['count'] += 1
        sensor_totals[event.sensor_id] = totals
        
        avg = totals['sum'] / totals['count']
        # emit result
        await avg_topic.send(value=SensorAvg(sensor_id=event.sensor_id, avg=avg))
        print(f"Sensor {event.sensor_id}: running avg = {avg:.2f}")

if __name__ == '__main__':
    app.main()
