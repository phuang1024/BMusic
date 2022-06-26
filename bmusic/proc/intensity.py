from .procedure import Procedure


class Intensity(Procedure):
    """
    Animates intensity of something, e.g. glow of a string.
    """

    def __init__(self, **kwargs):
        """
        Parameters
        ----------

        animators: List of Animator objects corresponding to properties
            to animate.

        min: Minimum intensity for all animators.

        max: Maximum intensity for all animators.
        """
        super().__init__(**kwargs)
        self.animators = kwargs.get("animators", [])
        self.min = kwargs.get("min", 0)
        self.max = kwargs.get("max", 1)

    def animate(self):
        self.animators[0].animate(0, 0)  # TODO test
