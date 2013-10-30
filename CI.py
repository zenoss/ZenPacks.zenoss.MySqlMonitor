import os
import time


def main():
    while True:
        run_time = time.time()
        status = os.system('make test')
        run_time = time.time() - run_time
        print '!' * 100, run_time
        if status == 2:
            print 'Looks like Ctrl+C. Stopping.'
            return
        if status == 0:
            os.system('notify-send -t 1000 OK "all tests passed. '
                      'Run time: %s s"' % int(run_time))

            print '\n'*5, 'Now wait a minute...'
            time.sleep(60)
        else:
            os.system('notify-send -t %s FAIL "something wrong with the code"'
                      % int(run_time * 1000))

if __name__ == '__main__':
    main()
