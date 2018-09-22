class Static:

    @staticmethod
    def update_last_10(customer_id, last10):
        if customer_id in last10:
            last10.remove(customer_id)

        last10.insert(0, customer_id)
        if len(last10) > 10:
            del last10[10]

    @staticmethod
    def dow_schedule(day):
        if day == 0:
            return 'Sunday'
        elif day == 1:
            return 'Monday'
        elif day == 2:
            return 'Tuesday'
        elif day == 3:
            return 'Wednesday'
        elif day == 4:
            return 'Thursday'
        elif day == 5:
            return 'Friday'
        else:
            return 'Saturday'

    @staticmethod
    def dow(day):
        if day == 0:
            return 'Mon'
        elif day == 1:
            return 'Tue'
        elif day == 2:
            return 'Wed'
        elif day == 3:
            return 'Thu'
        elif day == 4:
            return 'Fri'
        elif day == 5:
            return 'Sat'
        else:
            return 'Sun'

    @staticmethod
    def us_dollar(amount):
        dollar = amount
        try:
            dollar = '${:,.2f}'.format(amount)
        except TypeError:
            return amount
        except ValueError:
            return amount
        finally:
            return dollar

    @staticmethod
    def color_rgba(href):
        if href == '#000000' or href == 'Black' or href == '#000000ff':  # black
            return (0, 0, 0, 1)
        elif href == '#ffffff' or href == 'White' or href == '#ffffffff':  # white
            return (1, 1, 1, 1)
        elif href == '#0433ff' or href == 'Blue' or href == '#1952ffff':  # blue
            return (0.01568627, 0.2, 1, 1)
        elif href == '#aa7942' or href == 'Brown' or href == '#654321ff':  # brown
            return (0.667, 0.47450980, 0.25882353, 1)
        elif href == '#00f900' or href == 'Green' or href == '#36ff19ff':  # green
            return (0, 0.97647059, 0, 1)
        elif href == '#ff40ff' or href == 'Pink' or href == '#ff19c5ff':  # pink
            return (1, 0.25098039, 1, 1)
        elif href == '#ff9300' or href == 'Orange' or href == '#ff6f19ff':  # orange
            return (1, 0.57647059, 0, 1)
        elif href == '#942192' or href == 'Purple' or href == '#8c19ffff':  # purple
            return (0.58039216, 0.12941176, 0.57254902, 1)
        elif href == '#ff2600' or href == 'ff0000' or href == 'Red' or href == '#ff1919ff':  # red
            return (1, 0, 0, 1)
        elif href == '#fffb00' or href == 'Yellow' or href == '#e2ff19ff':  # yellow
            return (1, 0.98431373, 0, 1)
        elif href == '#000080ff' or href == 'Navy':  # navy
            return (0, 0, 0.50196078, 1)
        elif href == '#d2b48cff' or href == 'Tan':  # tan
            return (0.82352941, 0.70588235, 0.54901961, 1)
        elif href == '#d3d3d3ff' or href == 'Gray':  # gray
            return (0.82745098, 0.82745098, 0.82745098, 1)
        else:
            return (0, 0, 0, 1)

    @staticmethod
    def month_by_number(num):
        if num == 1:
            return 'January'
        elif num == 2:
            return 'February'
        elif num == 3:
            return 'March'
        elif num == 4:
            return 'April'
        elif num == 5:
            return 'May'
        elif num == 6:
            return 'June'
        elif num == 7:
            return 'July'
        elif num == 8:
            return 'August'
        elif num == 9:
            return 'September'
        elif num == 10:
            return 'October'
        elif num == 11:
            return 'November'
        else:
            return 'December'

    @staticmethod
    def get_starch_by_code(code):
        if code == 4:
            starch = 'Heavy'
        elif code == 2:
            starch = 'Light'
        elif code == 3:
            starch = 'Medium'
        else:
            starch = 'None'

        return starch

    @staticmethod
    def esc(command):
        if 'initiate':
            return b'\x1b' + b'@'
