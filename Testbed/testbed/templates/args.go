package templates

type Zone struct {
	QName    string
	ZoneFile string
}

type NameServer struct {
	Zones []*Zone
}

type Resolver struct {
	QMin string
}

type ZoneFile struct {
	QName    string
	NS       string
	ID       string
	SubZones []*SubZone
}

type SubZone struct {
	Label string
	NS    string
}
