package testbed

import (
	"os"
	"testbed/config"
	"text/template"
)

type Zone struct {
	NS             *Nameserver
	QName          string
	ID             string
	ZoneFileHost   string
	ZoneFileTarget string
}

func newZone(zoneConfig *config.Zone) *Zone {
	return &Zone{
		QName:          zoneConfig.QName,
		ID:             zoneConfig.ID,
		ZoneFileHost:   zoneConfig.ZoneFileHost,
		ZoneFileTarget: zoneConfig.ZoneFileTarget,
	}
}

func (z *Zone) set(zoneFile string) {
	tmpl, err := template.ParseFiles(zoneFile)
	if err != nil {
		panic(err)
	}
	dest, err := os.Create(z.ZoneFileHost)
	if err != nil {
		panic(err)
	}
	err = tmpl.Execute(dest, nil)
	if err != nil {
		return
	}
}
