package config

import (
	"errors"
	"fmt"
	"path/filepath"
)

type implementation struct {
	Name            string
	Version         string
	ConfigTarget    string
	RootHintsTarget string
	LogsTarget      string
	QMinParameter   map[bool]string
	StartCommands   []string
	StartDNSCap     string
}

func getImplementation(name, version string) (*implementation, error) {
	switch name {
	case "bind":
		return bind(version)
	case "unbound":
		return unbound(version)
	case "powerdns":
		return powerdns(version)
	default:
		panic(errors.New(fmt.Sprintf("implementation %s not available", name)))
	}
}

func bind(version string) (*implementation, error) {
	var err error
	/*var validatedVersion string
	supportedVersions := map[string]string{
		"9.11": "9.11.37",
		"9.16": "9.16.36",
		"9.17": "9.17.22",
		"9.18": "9.18.10",
		"9.19": "9.19.8",
	}
	if val, ok := supportedVersions[version]; ok {
		validatedVersion = val
	} else {
		validatedVersion = "9.18.4"
		err = errors.New(fmt.Sprintf("bind version %s is not supported (only major versions supported); fallback to version %s", version, validatedVersion))
	}*/
	logsTarget := filepath.Join("/etc", "logs")
	return &implementation{
		Name:            "bind",
		Version:         version,
		ConfigTarget:    filepath.Join("/etc", "bind"),
		RootHintsTarget: filepath.Join("/usr", "share", "dns", "root.hints"),
		LogsTarget:      logsTarget,
		QMinParameter: map[bool]string{
			true:  "relaxed",
			false: "off",
		},
		StartCommands: []string{
			"rndc-confgen -a",
			"named -u bind -4 -d 2",
		},
		StartDNSCap: fmt.Sprintf("dnscap -g 2> %s", filepath.Join(logsTarget, "trace.txt")),
	}, err
}

func powerdns(version string) (*implementation, error) {
	var err error
	var validatedVersion string
	supportedVersions := map[string]string{
		"4.2": "42",
		"4.3": "43",
		"4.4": "44",
		"4.5": "45",
		"4.6": "46",
		"4.7": "47",
		"4.8": "48",
	}
	if val, ok := supportedVersions[version]; ok {
		validatedVersion = val
	} else {
		validatedVersion = "47"
		err = errors.New(fmt.Sprintf("powerdns version %s is not supported (only major versions supported); fallback to version %s", version, validatedVersion))
	}
	logsTarget := filepath.Join("/etc", "powerdns", "logs")
	return &implementation{
		Name:            "powerdns",
		Version:         validatedVersion,
		ConfigTarget:    filepath.Join("/etc", "powerdns", "recursor.d"),
		RootHintsTarget: filepath.Join("/usr", "share", "dns", "myroot.hints"),
		LogsTarget:      logsTarget,
		QMinParameter: map[bool]string{
			true:  "yes",
			false: "no",
		},
		StartCommands: []string{
			"service pdns-recursor start",
		},
		StartDNSCap: fmt.Sprintf("dnscap -g 2> %s", filepath.Join(logsTarget, "trace.txt")),
	}, err
}

func unbound(version string) (*implementation, error) {
	var err error
	/*var validatedVersion string
	supportedVersions := map[string]string{
		"1.10": "1.10.1",
		"1.11": "1.11.0",
		"1.12": "1.12.0",
		"1.13": "1.13.2",
		"1.14": "1.14.0",
		"1.15": "1.15.0",
		"1.16": "1.16.3",
		"1.17": "1.17.0",
	}
	if val, ok := supportedVersions[version]; ok {
		validatedVersion = val
	} else {
		validatedVersion = "1.16.3"
		err = errors.New(fmt.Sprintf("unbound version %s is not supported (only major versions supported); fallback to version %s", version, validatedVersion))
	}*/
	logsTarget := filepath.Join("/usr", "local", "etc", "logs")
	return &implementation{
		Name:            "unbound",
		Version:         version,
		ConfigTarget:    filepath.Join("/usr", "local", "etc", "unbound"),
		RootHintsTarget: filepath.Join("/usr", "local", "etc", "unbound", "db.root"),
		LogsTarget:      logsTarget,
		QMinParameter: map[bool]string{
			true:  "yes",
			false: "no",
		},
		StartCommands: []string{
			"unbound-control-setup",
			"unbound-control start",
		},
		StartDNSCap: fmt.Sprintf("dnscap -g 2> %s", filepath.Join(logsTarget, "trace.txt")),
	}, err
}
