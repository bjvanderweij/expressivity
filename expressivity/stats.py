import scoremodel as sm
import tools

(features, expression) = tools.chooseFeatures()
sm.scoremodel(features, expression)
