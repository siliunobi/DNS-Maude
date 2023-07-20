package testbed

type Implementation interface {
	flushCache() error
	reload() error
	start() error
	filterQueries(queryLog []byte) []byte
	SetConfig(qmin, reload bool) error
}
