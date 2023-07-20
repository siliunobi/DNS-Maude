package config

import (
	"path/filepath"
	"time"
)

type Experiment struct {
	Name         string
	ResolverIDs  []string
	ZonesDir     string
	Delay        []int
	DelayedZones []string
	Target       string
	Measure      string
	Queries      []*query
	Warmup       []string
	QMin         bool
	Dest         string
	SaveLogs     bool
	Timeout      time.Duration
	Testbed      string
}

type query struct {
	Zone   string
	Record string
}

func (c *Config) LoadExperimentConfig(path string) (*Experiment, error) {
	c.v.SetDefault("saveLogs", true)
	c.v.SetDefault("delay", []int{0})
	c.v.SetConfigFile(path)
	if err := c.v.ReadInConfig(); err != nil {
		return nil, err
	}
	experimentConfig := &Experiment{}
	if err := c.v.Unmarshal(experimentConfig); err != nil {
		return nil, err
	}
	if experimentConfig.Testbed == "" {
		experimentConfig.Testbed = filepath.Join(filepath.Dir(path), "testbed.yaml")
	}
	if experimentConfig.ZonesDir == "" {
		experimentConfig.ZonesDir = filepath.Join(filepath.Dir(path), "zones")
	}
	if experimentConfig.Dest == "" {
		experimentConfig.Dest = filepath.Join(filepath.Dir(path), "results")
	}
	return experimentConfig, nil
}
