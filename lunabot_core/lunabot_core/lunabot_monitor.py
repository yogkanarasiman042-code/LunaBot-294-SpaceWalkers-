import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, String


class LunaBotMonitor(Node):

    def __init__(self):
        super().__init__('lunabot_monitor')

        # Safe habitat limits
        self.min_temperature = 15.0
        self.max_temperature = 30.0

        self.min_oxygen = 19.5
        self.max_oxygen = 23.5

        # Sensor subscriptions
        self.create_subscription(
            Float32,
            '/lunabot/temperature',
            self.temperature_callback,
            10
        )

        self.create_subscription(
            Float32,
            '/lunabot/oxygen',
            self.oxygen_callback,
            10
        )

        # Alert publisher
        self.alert_publisher = self.create_publisher(
            String,
            '/lunabot/alert',
            10
        )

        self.get_logger().info('🌙 LunaBot Environmental Monitor Started')
        self.get_logger().info('Monitoring temperature and oxygen levels...')

    def temperature_callback(self, msg):

        temperature = msg.data

        self.get_logger().info(
            f'Temperature: {temperature:.1f} °C'
        )

        if temperature < self.min_temperature:
            self.send_alert(
                f'LOW TEMPERATURE: {temperature:.1f} °C'
            )

        elif temperature > self.max_temperature:
            self.send_alert(
                f'HIGH TEMPERATURE: {temperature:.1f} °C'
            )

    def oxygen_callback(self, msg):

        oxygen = msg.data

        self.get_logger().info(
            f'Oxygen: {oxygen:.1f} %'
        )

        if oxygen < self.min_oxygen:
            self.send_alert(
                f'LOW OXYGEN: {oxygen:.1f} %'
            )

        elif oxygen > self.max_oxygen:
            self.send_alert(
                f'ABNORMAL OXYGEN: {oxygen:.1f} %'
            )

    def send_alert(self, message):

        alert = String()
        alert.data = message

        self.alert_publisher.publish(alert)

        self.get_logger().error(
            f'🚨 ANOMALY DETECTED — {message}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = LunaBotMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
