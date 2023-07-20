package testbed

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"testbed/testbed/templates"
	"text/template"
)

type powerDNS struct {
	templatesDir string
	container    *Container
}

func newPowerDNS(templatesDir string, container *Container) powerDNS {
	return powerDNS{
		templatesDir: templatesDir,
		container:    container,
	}
}

func (p powerDNS) reload() error {
	execResult, err := p.container.Exec([]string{"service", "pdns-recursor", "restart"})
	if err != nil {
		return err
	}
	matched, err := regexp.MatchString("done\n$", execResult.StdOut)
	if err != nil {
		return err
	}
	if !matched {
		err = errors.New(fmt.Sprintf("powerDNS could not be started successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
		return err
	}
	return nil
}

func (p powerDNS) start() error {
	execResult, err := p.container.Exec([]string{"service", "pdns-recursor", "start"})
	if err != nil {
		panic(err)
	}
	matched, err := regexp.MatchString("$done\n$", execResult.StdOut)
	if err != nil {
		panic(err)
	}
	if !matched {
		return errors.New(fmt.Sprintf("powerDNS could not be started successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
	}
	return nil
}

func (p powerDNS) flushCache() error {
	return p.reload()
}

func (p powerDNS) filterQueries(queryLog []byte) []byte {
	//TODO implement
	return queryLog
}

func (p powerDNS) SetConfig(qmin, reload bool) error {
	tmpl, err := template.ParseFiles(filepath.Join(p.templatesDir, "additional.conf"))
	if err != nil {
		panic(err)
	}
	dest, err := os.Create(filepath.Join(p.container.Config, "additional.conf"))
	if err != nil {
		panic(err)
	}
	options := &templates.Resolver{
		QMin: "no",
	}
	if qmin {
		options.QMin = "yes"
	}
	err = tmpl.Execute(dest, options)
	if err != nil {
		panic(err)
	}
	if reload {
		err := p.reload()
		if err != nil {
			return err
		}
	}
	return nil
}
