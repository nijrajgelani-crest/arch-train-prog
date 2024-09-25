from threading import Lock, Thread


lock_a = Lock()
lock_b = Lock()


def thread_a():
    with lock_a:
        print("Thread A acquired lock A")
        with lock_b:
            print("Thread A acquired lock B")


def thread_b():
    with lock_b:
        print("Thread B acquired lock B")
        with lock_a:
            print("Thread B acquired lock A")


t1 = Thread(target=thread_a)
t2 = Thread(target=thread_b)

t1.start()
t2.start()

t1.join()
t2.join()
