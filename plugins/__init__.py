from airflow.plugins_manager import AirflowPlugin
from hooks.selenium_hook \
    import SeleniumHook
from operators.selenium_operator \
    import SeleniumOperator


class SeleniumPlugin(AirflowPlugin):
    name = 'selenium_plugin'
    operators = [SeleniumOperator]
    hooks = [SeleniumHook]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []