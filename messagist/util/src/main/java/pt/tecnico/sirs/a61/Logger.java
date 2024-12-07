package pt.tecnico.sirs.a61;

/**
 * Used to log information.
 */
public class Logger {
    boolean _debug;

    public Logger() {
        _debug = false;
    }

    public Logger(boolean debug) {
        _debug = debug;
    }

    public void setDebug(boolean debug) {
        _debug = debug;
    }

    public void log(String msg) {
        System.out.println(msg);
    }

    public void debug(String msg) {
        if (_debug) {
            log("[DEBUG]: " + msg);
        }
    }
}
