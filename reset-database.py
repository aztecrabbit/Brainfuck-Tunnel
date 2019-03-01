import app


def main():
    app.log('Reseting Database')
    app.reset_database()
    app.log('Reseting Database Complete \n')

if __name__ == '__main__':
    main()
