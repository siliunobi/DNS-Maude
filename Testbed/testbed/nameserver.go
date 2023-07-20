package testbed

import (
	"errors"
	"fmt"
	"testbed/config"
	"time"
)

type Nameserver struct {
	*Container
	Implementation
	Zones map[string]*Zone
}

func newNameServer(nameserverConfig *config.Nameserver, templates string) *Nameserver {
	container := NewContainer(nameserverConfig.ID, nameserverConfig.Dir, nameserverConfig.IP)
	impl := newBind(templates, container)
	zones := make(map[string]*Zone)
	for _, zoneConfig := range nameserverConfig.Zones {
		zones[zoneConfig.ID] = newZone(zoneConfig)
	}
	return &Nameserver{
		Container:      container,
		Implementation: impl,
		Zones:          zones,
	}
}

func (n *Nameserver) SetZone(zoneID, zoneFile string) {
	n.Zones[zoneID].set(zoneFile)
	err := n.reload()
	if err != nil {
		panic(err)
	}
}

func (n *Nameserver) SetDelay(duration time.Duration) {
	execResult, err := n.Exec([]string{"tc", "qdisc", "change", "dev", "eth0", "root", "netem", "delay", fmt.Sprintf("%dms", duration.Milliseconds())})
	if err != nil {
		panic(err)
	}
	if execResult.StdOut != "" {
		err = errors.New(fmt.Sprintf("could not set delay at %s: %s", n.ID, execResult.StdOut))
		panic(err)
	}
}
