import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class EnvironmentSensor(Node):

    def __init__(self):
        super().__init__('environment_sensor')

        self.temperature_publisher = self.create_publisher(
            Float32,
            '/lunabot/temperature',
            10
        )

        self.oxygen_publisher = self.create_publisher(
            Float32,
            '/lunabot/oxygen',
            10
        )

        self.timer = self.create_timer(1.0, self.publish_sensor_data)

        # Normal habitat conditions
        self.temperature = 22.0
        self.oxygen = 20.9

        self.get_logger().info(
            '🌡️ LunaBot Environment Sensor Started'
        )

    def publish_sensor_data(self):

        temperature_msg = Float32()
        temperature_msg.data = self.temperature

        oxygen_msg = Float32()
        oxygen_msg.data = self.oxygen

        self.temperature_publisher.publish(temperature_msg)
        self.oxygen_publisher.publish(oxygen_msg)


def main(args=None):

    rclpy.init(args=args)

    node = EnvironmentSensor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
