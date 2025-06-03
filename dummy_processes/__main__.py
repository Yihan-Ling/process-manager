from time import sleep

from node import launch, watch

# ps = launch('igmr_robotics_toolkit.comms.params')
# sleep(1)

# watch(
#     ps,
#     launch('RAOCTg2.face_tracker'),
#     launch('RAOCTg2.pupil_tracker'),
#     launch('RAOCTg2.robot_controller'),
#     launch('igmr_robotics_toolkit.node.speech'),
# )

watch(
    launch('d_one'),
    launch('d_two'),
    launch('d_three')
)