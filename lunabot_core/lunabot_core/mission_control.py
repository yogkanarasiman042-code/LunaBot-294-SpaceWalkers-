import tkinter as tk
from datetime import datetime
import subprocess

import cv2
import rclpy

from cv_bridge import CvBridge
from PIL import Image as PILImage
from PIL import ImageTk

from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, String


class MissionControlNode(Node):

    def __init__(self, ui):
        super().__init__('lunabot_mission_control')

        self.ui = ui
        self.bridge = CvBridge()
                # Nav2 arbitrary goal client
        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

        # =================================================
        # SUBSCRIBERS
        # =================================================

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

        self.create_subscription(
            String,
            '/lunabot/mission_status',
            self.mission_callback,
            10
        )

        self.create_subscription(
            String,
            '/lunabot/alert',
            self.alert_callback,
            10
        )

        self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )

        # =================================================
        # DEMO PUBLISHERS
        # =================================================

        self.temp_pub = self.create_publisher(
            Float32,
            '/lunabot/temperature',
            10
        )

        self.oxygen_pub = self.create_publisher(
            Float32,
            '/lunabot/oxygen',
            10
        )

    # =====================================================
    # SENSOR CALLBACKS
    # =====================================================
    def send_navigation_goal(self, x, y):

        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.ui.add_event(
                'Nav2 navigation server unavailable'
            )
            return

        goal = NavigateToPose.Goal()

        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        goal.pose.pose.position.z = 0.0

        goal.pose.pose.orientation.x = 0.0
        goal.pose.pose.orientation.y = 0.0
        goal.pose.pose.orientation.z = 0.0
        goal.pose.pose.orientation.w = 1.0

        self.nav_client.send_goal_async(goal)

        self.ui.add_event(
            f'Operator goal sent: ({x:.2f}, {y:.2f})'
        )

    def temperature_callback(self, msg):
        self.ui.temperature = msg.data

    def oxygen_callback(self, msg):
        self.ui.oxygen = msg.data

    # =====================================================
    # MISSION CALLBACK
    # =====================================================

    def mission_callback(self, msg):

        parts = {}

        for item in msg.data.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                parts[key] = value

        self.ui.priority_zone = parts.get(
            'PRIORITY',
            self.ui.priority_zone
        )

        self.ui.risk = parts.get(
            'RISK',
            self.ui.risk
        )

        target_x = parts.get(
            'TARGET_X',
            '0.00'
        )

        target_y = parts.get(
            'TARGET_Y',
            '0.00'
        )

        self.ui.target = (
            f'({target_x}, {target_y})'
        )

    # =====================================================
    # ALERT CALLBACK
    # =====================================================

    def alert_callback(self, msg):

        self.ui.alert_message = msg.data

        self.ui.add_event(
            f'ALERT: {msg.data}'
        )

    # =====================================================
    # CAMERA CALLBACK
    # =====================================================

    def camera_callback(self, msg):

        try:

            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            self.ui.latest_camera_frame = frame.copy()

        except Exception as e:

            self.get_logger().error(
                f'Camera conversion error: {e}'
            )


class LunaBotMissionControl:

    def __init__(self):

        # =================================================
        # WINDOW
        # =================================================

        self.root = tk.Tk()

        self.root.title(
            'LunaBot Mission Control'
        )

        self.root.geometry(
            '1200x720'
        )

        self.root.minsize(
            1100,
            680
        )

        # =================================================
        # RUNTIME VALUES
        # =================================================

        self.temperature = 22.0
        self.oxygen = 20.9

        self.priority_zone = 'NONE'
        self.risk = '0'
        self.target = '(0.00, 0.00)'

        self.alert_message = (
            'Habitat conditions nominal'
        )

        self.camera_image = None
        self.latest_camera_frame = None

        self.patrol_process = None

        # =================================================
        # HEADER
        # =================================================

        header = tk.Frame(
            self.root,
            bg='#111827',
            height=85
        )

        header.pack(
            fill='x'
        )

        tk.Label(
            header,
            text='LUNABOT MISSION CONTROL',
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#111827'
        ).pack(
            pady=(14, 0)
        )

        tk.Label(
            header,
            text='Risk-Aware Autonomous Lunar Habitat Operations',
            font=('Arial', 11),
            fg='#cbd5e1',
            bg='#111827'
        ).pack()

        # =================================================
        # MAIN LAYOUT
        # =================================================

        main = tk.Frame(
            self.root,
            padx=15,
            pady=15
        )

        main.pack(
            fill='both',
            expand=True
        )

        left = tk.Frame(main)
        right = tk.Frame(main)

        left.pack(
            side='left',
            fill='both',
            expand=True,
            padx=(0, 10)
        )

        right.pack(
            side='right',
            fill='both',
            expand=True,
            padx=(10, 0)
        )

        # =================================================
        # CAMERA PANEL
        # =================================================

        camera_frame = tk.LabelFrame(
            left,
            text='ROVER CAMERA',
            padx=10,
            pady=10
        )

        camera_frame.pack(
            fill='both',
            expand=True
        )

        self.camera_label = tk.Label(
            camera_frame,
            text='CAMERA FEED\n/camera/image_raw',
            font=('Arial', 18, 'bold'),
            bg='black',
            fg='white'
        )

        self.camera_label.pack(
            fill='both',
            expand=True
        )

        # =================================================
        # MISSION CONTROLS
        # =================================================

        control_frame = tk.LabelFrame(
            left,
            text='MISSION CONTROLS',
            padx=10,
            pady=10
        )

        control_frame.pack(
            fill='x',
            pady=(12, 0)
        )

        tk.Button(
            control_frame,
            text='START PATROL',
            command=self.start_patrol,
            width=16,
            height=2
        ).pack(
            side='left',
            padx=4
        )

        tk.Button(
            control_frame,
            text='STOP PATROL',
            command=self.stop_patrol,
            width=16,
            height=2
        ).pack(
            side='left',
            padx=4
        )

        tk.Button(
            control_frame,
            text='SIMULATE HIGH TEMP',
            command=self.simulate_high_temp,
            width=19,
            height=2
        ).pack(
            side='left',
            padx=4
        )

        tk.Button(
            control_frame,
            text='RESET ENVIRONMENT',
            command=self.reset_environment,
            width=19,
            height=2
        ).pack(
            side='left',
            padx=4
        )
             # =================================================
        # OPERATOR GOAL NAVIGATION
        # =================================================

        goal_frame = tk.Frame(left)

        goal_frame.pack(
            fill='x',
            pady=(8, 0)
        )

        tk.Label(
            goal_frame,
            text='TARGET X:'
        ).pack(
            side='left',
            padx=(4, 2)
        )

        self.goal_x_entry = tk.Entry(
            goal_frame,
            width=8
        )

        self.goal_x_entry.pack(
            side='left',
            padx=3
        )

        tk.Label(
            goal_frame,
            text='TARGET Y:'
        ).pack(
            side='left',
            padx=(10, 2)
        )

        self.goal_y_entry = tk.Entry(
            goal_frame,
            width=8
        )

        self.goal_y_entry.pack(
            side='left',
            padx=3
        )

        tk.Button(
            goal_frame,
            text='GO TO TARGET',
            command=self.go_to_target,
            width=18,
            height=2
        ).pack(
            side='left',
            padx=10
        )

        # =================================================
        # HABITAT STATUS
        # =================================================

        status_frame = tk.LabelFrame(
            right,
            text='HABITAT STATUS',
            padx=15,
            pady=15
        )

        status_frame.pack(
            fill='x'
        )

        self.temp_label = tk.Label(
            status_frame,
            text='Temperature: -- °C',
            font=('Arial', 16)
        )

        self.temp_label.pack(
            anchor='w',
            pady=5
        )

        self.oxygen_label = tk.Label(
            status_frame,
            text='Oxygen: -- %',
            font=('Arial', 16)
        )

        self.oxygen_label.pack(
            anchor='w',
            pady=5
        )

        self.habitat_label = tk.Label(
            status_frame,
            text='STATUS: SAFE',
            font=('Arial', 16, 'bold')
        )

        self.habitat_label.pack(
            anchor='w',
            pady=8
        )

        # =================================================
        # MISSION STATUS
        # =================================================

        mission_frame = tk.LabelFrame(
            right,
            text='MISSION STATUS',
            padx=15,
            pady=15
        )

        mission_frame.pack(
            fill='x',
            pady=(12, 0)
        )

        self.priority_label = tk.Label(
            mission_frame,
            text='Priority Zone: NONE',
            font=('Arial', 14)
        )

        self.priority_label.pack(
            anchor='w',
            pady=4
        )

        self.risk_label = tk.Label(
            mission_frame,
            text='Risk Score: 0',
            font=('Arial', 14)
        )

        self.risk_label.pack(
            anchor='w',
            pady=4
        )

        self.target_label = tk.Label(
            mission_frame,
            text='Target: (0.00, 0.00)',
            font=('Arial', 14)
        )

        self.target_label.pack(
            anchor='w',
            pady=4
        )

        # =================================================
        # ALERT STATUS
        # =================================================

        alert_frame = tk.LabelFrame(
            right,
            text='ALERT STATUS',
            padx=15,
            pady=15
        )

        alert_frame.pack(
            fill='x',
            pady=(12, 0)
        )

        self.alert_label = tk.Label(
            alert_frame,
            text='Habitat conditions nominal',
            font=('Arial', 13, 'bold'),
            wraplength=450
        )

        self.alert_label.pack(
            anchor='w'
        )

        # =================================================
        # EVENT LOG
        # =================================================

        log_frame = tk.LabelFrame(
            right,
            text='EVENT LOG',
            padx=10,
            pady=10
        )

        log_frame.pack(
            fill='both',
            expand=True,
            pady=(12, 0)
        )

        self.event_log = tk.Text(
            log_frame,
            height=8,
            state='disabled'
        )

        self.event_log.pack(
            fill='both',
            expand=True
        )

        self.add_event(
            'Mission Control initialized'
        )

        # =================================================
        # ROS
        # =================================================

        rclpy.init()

        self.ros_node = MissionControlNode(
            self
        )

        self.root.after(
            100,
            self.ros_spin
        )

        self.root.after(
            100,
            self.update_ui
        )

        self.root.protocol(
            'WM_DELETE_WINDOW',
            self.on_close
        )

    # =====================================================
    # ROS LOOP
    # =====================================================

    def ros_spin(self):

        if rclpy.ok():

            rclpy.spin_once(
                self.ros_node,
                timeout_sec=0.0
            )

            self.root.after(
                20,
                self.ros_spin
            )

    # =====================================================
    # UI UPDATE
    # =====================================================

    def update_ui(self):

        self.temp_label.config(
            text=f'Temperature: {self.temperature:.1f} °C'
        )

        self.oxygen_label.config(
            text=f'Oxygen: {self.oxygen:.1f} %'
        )

        self.priority_label.config(
            text=f'Priority Zone: {self.priority_zone}'
        )

        self.risk_label.config(
            text=f'Risk Score: {self.risk}'
        )

        self.target_label.config(
            text=f'Target: {self.target}'
        )

        # LIVE CAMERA

        if self.latest_camera_frame is not None:

            frame = cv2.resize(
                self.latest_camera_frame,
                (500, 350)
            )

            image = PILImage.fromarray(
                frame
            )

            self.camera_image = ImageTk.PhotoImage(
                image=image
            )

            self.camera_label.config(
                image=self.camera_image,
                text=''
            )

        # SAFETY STATE

        unsafe = (
            self.temperature > 35.0
            or self.temperature < 5.0
            or self.oxygen < 19.5
            or self.oxygen > 23.5
        )

        if unsafe:

            self.habitat_label.config(
                text='STATUS: CRITICAL',
                fg='red'
            )

            self.alert_label.config(
                text=self.alert_message,
                fg='red'
            )

        else:

            self.habitat_label.config(
                text='STATUS: SAFE',
                fg='green'
            )

            self.alert_label.config(
                text='Habitat conditions nominal',
                fg='green'
            )

        self.root.after(
            100,
            self.update_ui
        )

    # =====================================================
    # PATROL CONTROLS
    # =====================================================
    def go_to_target(self):

        try:
            x = float(self.goal_x_entry.get())
            y = float(self.goal_y_entry.get())

        except ValueError:
            self.add_event(
                'Invalid target coordinates'
            )
            return

        # Stop autonomous patrol before accepting
        # an operator-selected navigation target
        if (
            self.patrol_process is not None
            and self.patrol_process.poll() is None
        ):
            self.patrol_process.terminate()

            self.add_event(
                'Patrol stopped for operator navigation'
            )

        self.add_event(
            f'Operator requested target: ({x:.2f}, {y:.2f})'
        )

        self.ros_node.send_navigation_goal(
            x,
            y
        )
    def start_patrol(self):

        if (
            self.patrol_process is not None
            and self.patrol_process.poll() is None
        ):

            self.add_event(
                'Patrol already running'
            )

            return

        try:

            self.patrol_process = subprocess.Popen(
                [
                    'ros2',
                    'run',
                    'lunabot_core',
                    'lunabot_patrol'
                ]
            )

            self.add_event(
                'Autonomous patrol started'
            )

        except Exception as e:

            self.add_event(
                f'Unable to start patrol: {e}'
            )

    def stop_patrol(self):

        if (
            self.patrol_process is not None
            and self.patrol_process.poll() is None
        ):

            self.patrol_process.terminate()

            self.add_event(
                'Autonomous patrol stopped'
            )

        else:

            self.add_event(
                'No active patrol process'
            )

    # =====================================================
    # DEMONSTRATION CONTROLS
    # =====================================================

    def simulate_high_temp(self):

        msg = Float32()
        msg.data = 40.0

        self.alert_message = (
            'HIGH TEMPERATURE ANOMALY DETECTED: 40.0 °C'
        )

        self.ros_node.temp_pub.publish(
            msg
        )

        self.add_event(
            'High-temperature anomaly injected: 40.0 °C'
        )

    def reset_environment(self):

        # Restore normal habitat temperature
        temp_msg = Float32()
        temp_msg.data = 22.0

        # Restore normal oxygen level
        oxygen_msg = Float32()
        oxygen_msg.data = 20.9

        # Publish restored environmental values
        self.ros_node.temp_pub.publish(temp_msg)
        self.ros_node.oxygen_pub.publish(oxygen_msg)

        # Restore UI alert state
        self.alert_message = (
            'Habitat conditions nominal'
        )

        # Record reset in Mission Control event log
        self.add_event(
            'Environment restored to nominal conditions'
        )
    def add_event(self, message):

        timestamp = datetime.now().strftime(
            '%H:%M:%S'
        )

        self.event_log.config(
            state='normal'
        )

        self.event_log.insert(
            'end',
            f'[{timestamp}] {message}\n'
        )

        self.event_log.see(
            'end'
        )

        self.event_log.config(
            state='disabled'
        )

    # =====================================================
    # CLEAN SHUTDOWN
    # =====================================================

    def on_close(self):

        if (
            self.patrol_process is not None
            and self.patrol_process.poll() is None
        ):

            self.patrol_process.terminate()

        self.ros_node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():

    app = LunaBotMissionControl()
    app.run()


if __name__ == '__main__':
    main()
