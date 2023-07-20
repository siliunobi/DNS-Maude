package config

import (
	"fmt"
	"path/filepath"
	"strings"
)

type ZoneInput struct {
	QName string
}

type Zone struct {
	ID             string
	QName          string
	ZoneFileHost   string
	ZoneFileTarget string
}

func (c *Config) newZone(build string, input *ZoneInput) (*Zone, error) {
	var err error
	id := GenerateZoneID(input.QName)
	return &Zone{
		ID:             id,
		QName:          input.QName,
		ZoneFileHost:   filepath.Join(build, "zones", fmt.Sprintf("%s.zone", id)),
		ZoneFileTarget: filepath.Join("/zones", fmt.Sprintf("%s.zone", id)),
	}, err
}

func GenerateZoneID(qname string) string {
	if qname == "." {
		return "root"
	}
	f := func(c rune) bool {
		return c == '.'
	}
	split := strings.FieldsFunc(qname, f)
	return strings.Join(split, "-")
}
