# -*- coding: utf-8 -*-

tools1 = [
    # Motion control
    {
        "type": "function",
        "function": {
            "name": "Navigate_To_Location",
            "description": "控制机器人**移动前往**某地点或区域（充电站、门口、坐标等）。"
                           "若用户只说停下、停止、别动、急停、站住，不要选本函数，应选 Stop_Movement。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Target_Location": {
                        "type": "string",
                        "description": "目标位置描述。若为语义位置则直接提取（如'充电站'、'工作台'、'原点'）；"
                                       "若为坐标则格式化为'x,y'形式。位置为空时停止导航。"
                    },
                    "Speed_Mode": {
                        "type": "string",
                        "description": "移动速度模式：'slow'慢速/谨慎，'normal'正常，'fast'快速。默认为normal。"
                    }
                },
                "required": ["Target_Location", "Speed_Mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Stop_Movement",
            "description": "立即停止机器人所有运动（用户说停下、停止、别动、急停、站住、不要再走了等）。"
                           "与 Navigate_To_Location 互斥：没有目标地点的纯停止指令必须选本函数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Stop_Mode": {
                        "type": "string",
                        "description": "停止模式：'emergency'紧急停止（立即），'normal'正常停止（减速后停）。"
                    }
                },
                "required": ["Stop_Mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Execute_Gait_Mode",
            "description": "切换机器人步态模式。适用于Go2四足或人形机器人运动模式切换。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Gait_Type": {
                        "type": "string",
                        "description": "步态类型：'walk'行走，'trot'小跑，'crawl'爬行（低矮障碍），"
                                       "'stand'站立，'sit'坐下，'lie'趴下。"
                    }
                },
                "required": ["Gait_Type"]
            }
        }
    },

    # Manipulation
    {
        "type": "function",
        "function": {
            "name": "Grasp_Object",
            "description": "**直接执行**抓取（如「抓红色盒子」「抓取水瓶」）。"
                           "用户若以怎么、如何、怎样、为什么开头询问方法或原理，不要选本函数（应不调用工具或选 Unknown）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Object_Name": {
                        "type": "string",
                        "description": "要抓取的物体名称，如'水瓶'、'工具箱'、'零件'等。"
                    },
                    "Grasp_Force": {
                        "type": "string",
                        "description": "抓取力度：'light'轻柔（易碎物品），'normal'正常，'firm'用力（重物）。默认normal。"
                    }
                },
                "required": ["Object_Name", "Grasp_Force"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Place_Object",
            "description": "将机械臂当前持有的物体放置到指定位置。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Target_Position": {
                        "type": "string",
                        "description": "放置目标位置，如'桌面'、'托盘'、'传送带'等语义位置或具体坐标。"
                    }
                },
                "required": ["Target_Position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Control_Arm_Pose",
            "description": "控制机械臂到达预设姿态或指定关节角度。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Pose_Name": {
                        "type": "string",
                        "description": "预设姿态名称：'home'初始位，'ready'准备位，'inspect'检测位，'rest'休息位。"
                                       "或直接描述动作意图。"
                    }
                },
                "required": ["Pose_Name"]
            }
        }
    },

    # Perception and status
    {
        "type": "function",
        "function": {
            "name": "Query_Robot_Status",
            "description": "查询机器人当前状态信息，包括电量、位置、关节温度、传感器数据等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Status_Type": {
                        "type": "string",
                        "description": "查询类型：'battery'电量，'position'位置，'temperature'温度，"
                                       "'all'全部状态，'sensor'传感器数据。"
                    }
                },
                "required": ["Status_Type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Scan_Environment",
            "description": "启动环境感知扫描，使用激光雷达或深度相机构建周围环境地图或检测障碍物。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Scan_Mode": {
                        "type": "string",
                        "description": "扫描模式：'obstacle'障碍物检测，'mapping'建图，'object_detect'目标检测，'full'全面扫描。"
                    },
                    "Range": {
                        "type": "string",
                        "description": "扫描范围：'near'近距离(1m内)，'medium'中距离(1-5m)，'far'远距离(5m+)。"
                    }
                },
                "required": ["Scan_Mode", "Range"]
            }
        }
    },

    # Tasks and return-to-base
    {
        "type": "function",
        "function": {
            "name": "Execute_Task_Sequence",
            "description": "执行预定义的任务序列，支持巡检、搬运、组装等复合任务。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Task_Name": {
                        "type": "string",
                        "description": "任务名称：'patrol'巡逻/巡检，'transport'搬运，'inspect'质检，'demo'演示。"
                    },
                    "Target_Object": {
                        "type": "string",
                        "description": "任务目标对象，若无则为空。如搬运任务的目标物品名称。"
                    }
                },
                "required": ["Task_Name", "Target_Object"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Return_To_Base",
            "description": "控制机器人返回基站/充电桩进行充电或待机。电量低时自动触发。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Mode": {
                        "type": "string",
                        "description": "返回模式：'charge'充电，'standby'待机，'emergency'紧急返回。"
                    }
                },
                "required": ["Mode"]
            }
        }
    },

    # ROS bridge
    {
        "type": "function",
        "function": {
            "name": "Publish_ROS_Command",
            "description": "通过ROS话题发布控制指令，适用于ROS生态系统中的任意机器人平台。",
            "parameters": {
                "type": "object",
                "properties": {
                    "Topic": {
                        "type": "string",
                        "description": "ROS话题名称，如'/cmd_vel'、'/joint_states'、'/arm_controller/command'等。"
                    },
                    "Command": {
                        "type": "string",
                        "description": "指令内容描述，系统将自动转换为对应ROS消息格式。"
                    }
                },
                "required": ["Topic", "Command"]
            }
        }
    },
]


# High-level intent groups (robot control)
INTENT_LABELS = {
    "NAVIGATION": ["Navigate_To_Location", "Stop_Movement", "Return_To_Base"],
    "LOCOMOTION": ["Execute_Gait_Mode"],
    "MANIPULATION": ["Grasp_Object", "Place_Object", "Control_Arm_Pose"],
    "PERCEPTION": ["Query_Robot_Status", "Scan_Environment"],
    "TASK": ["Execute_Task_Sequence", "Publish_ROS_Command"],
}

# Example utterances for debugging
EXAMPLE_DIALOGS = [
    {"user": "去充电站充电", "intent": "NAVIGATION", "function": "Return_To_Base", "args": {"Mode": "charge"}},
    {"user": "慢慢走到工作台旁边", "intent": "NAVIGATION", "function": "Navigate_To_Location", "args": {"Target_Location": "工作台", "Speed_Mode": "slow"}},
    {"user": "把桌上的水瓶轻轻拿起来", "intent": "MANIPULATION", "function": "Grasp_Object", "args": {"Object_Name": "水瓶", "Grasp_Force": "light"}},
    {"user": "现在电量还剩多少", "intent": "PERCEPTION", "function": "Query_Robot_Status", "args": {"Status_Type": "battery"}},
    {"user": "开始巡检任务", "intent": "TASK", "function": "Execute_Task_Sequence", "args": {"Task_Name": "patrol", "Target_Object": ""}},
    {"user": "立刻停下", "intent": "NAVIGATION", "function": "Stop_Movement", "args": {"Stop_Mode": "emergency"}},
    {"user": "切换到小跑步态", "intent": "LOCOMOTION", "function": "Execute_Gait_Mode", "args": {"Gait_Type": "trot"}},
    {"user": "扫描周围有没有障碍物", "intent": "PERCEPTION", "function": "Scan_Environment", "args": {"Scan_Mode": "obstacle", "Range": "medium"}},
]
