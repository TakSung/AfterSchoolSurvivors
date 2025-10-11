"""
Coordinate system conversion utilities for rendering.
"""

def to_pygame_angle(world_angle_degrees: float) -> float:
    """
    Converts a standard mathematical angle (Y-axis up) to a 
    Pygame screen angle (Y-axis down) by negating it.
    
    Args:
        world_angle_degrees: The angle in degrees from the world coordinate system.
        
    Returns:
        The angle in degrees adjusted for Pygame's screen coordinate system.
    """
    return -world_angle_degrees
