import time
#http://stackoverflow.com/a/160208

class AccurateTimeStamp():
    """
    A simple class to provide a very accurate means of time stamping some data
    """

    # Do the class-wide initial time stamp to synchronise calls to 
    # time.clock() to a single time stamp
    initialTimeStamp = time.time()+ time.clock()

    def __init__(self):
        """
        Constructor for the AccurateTimeStamp class.
        This makes a stamp based on the current time which should be more 
        accurate than anything you can get out of time.time().
        NOTE: This time stamp will only work if nothing has called clock() in
        this instance of the Python interpreter.
        """
        # Get the time since the first of call to time.clock()
        offset = time.clock()

        # Get the current (accurate) time
        currentTime = AccurateTimeStamp.initialTimeStamp+offset

        # Split the time into whole seconds and the portion after the fraction 
        self.accurateSeconds = int(currentTime)
        self.accuratePastSecond = currentTime - self.accurateSeconds


def GetAccurateTimeStampString(timestamp):
    """
    Function to produce a timestamp of the form "13:48:01.87123" representing 
    the time stamp 'timestamp'
    """
    # Get a struct_time representing the number of whole seconds since the 
    # epoch that we can use to format the time stamp
    wholeSecondsInTimeStamp = time.localtime(timestamp.accurateSeconds)

    # Convert the whole seconds and whatever fraction of a second comes after
    # into a couple of strings 
    wholeSecondsString = time.strftime("%H%M%S", wholeSecondsInTimeStamp)
    fractionAfterSecondString = str(int(timestamp.accuratePastSecond*1000000))

    # Return our shiny new accurate time stamp   
    return time.strftime("%d%m%y")+wholeSecondsString+"."+fractionAfterSecondString


if __name__ == '__main__':
    for i in range(0,500):
        timestamp = AccurateTimeStamp()
        print GetAccurateTimeStampString(timestamp)