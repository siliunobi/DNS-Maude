package config

import (
	"path/filepath"
	"strings"
)

type NameserverInput struct {
	IP    string
	ID    string
	Zones []*ZoneInput
}

type Nameserver struct {
	ID             string
	IP             string
	Zones          []*Zone
	Dir            string
	Logs           string
	Config         string
	Implementation *implementation
}

func (c *Config) newNameServer(build string, input *NameserverInput) (*Nameserver, error) {
	var zones []*Zone
	for _, zoneInput := range input.Zones {
		if !strings.HasSuffix(zoneInput.QName, ".") {
			zoneInput.QName += "."
		}
		zone, err := c.newZone(build, zoneInput)
		if err != nil {
			return nil, err
		}
		zones = append(zones, zone)
	}
	dir := filepath.Join(build, input.ID)
	var err error
	impl, err := bind("9.18.4")
	return &Nameserver{
		ID:             input.ID,
		IP:             input.IP,
		Zones:          zones,
		Dir:            dir,
		Logs:           filepath.Join(dir, "logs"),
		Config:         filepath.Join(dir, "config"),
		Implementation: impl,
	}, err
}
