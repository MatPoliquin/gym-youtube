# gym-youtube

Fork of gymI use to generate youtube videos of ML models playing games.
Example videos:
*   [https://www.youtube.com/watch?v=iedw_7yKgQI&list=PLmwlWbdWpZVvwxzxY1nJII6lEiXeMqLdP](https://www.youtube.com/watch?v=iedw_7yKgQI&list=PLmwlWbdWpZVvwxzxY1nJII6lEiXeMqLdP)


**Must be used with baselines-youtube to work**

Features:
*   Renders all frames of the game as opposed of 1 out of 4 frames that baselines saves
*   Videos include the game's sound
*   Displays CPU/GPU usage
*   Displays Reward Function output
*   Displays Model info such as type and number of parameters

Problems:
*   Model architecture display is hard coded
*   Code is very hacky overall

### Installation
```
git clone https://github.com/MatPoliquin/gym-youtube.git
cd gym-youtube
pip2 install -e .
```
