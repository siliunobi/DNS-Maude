package experiment

import (
	"fmt"
	"github.com/go-gota/gota/dataframe"
	"github.com/go-gota/gota/series"
	"github.com/schollz/progressbar/v3"
	"os"
	"path/filepath"
	"strings"
	"testbed/config"
	"testbed/testbed"
	"time"
)

type Experiment struct {
	config *config.Experiment
}

func New(experimentConfig *config.Experiment) *Experiment {
	return &Experiment{config: experimentConfig}
}

func (e *Experiment) Run(testbed *testbed.Testbed) error {
	/*err := testbed.Reset()
	if err != nil {
		for i := 0; i < 20; i++ {
			time.Sleep(2 * time.Second)
			err = testbed.Reset()
			if err == nil {
				break
			}
		}
		if err != nil {
			return err
		}
	}*/
	var dataResolver []string
	var dataZone []string
	var dataDelay []int
	var dataResult []int
	var dataQuery []string
	perm := os.FileMode(0777)
	if err := os.Mkdir(e.config.Dest, perm); err != nil {
		return err
	}
	logDir := filepath.Join(e.config.Dest, "logs")
	if err := os.Mkdir(logDir, perm); err != nil {
		return err
	}
	isVolume := e.config.Measure == "volume"
	isDuration := e.config.Measure == "duration"
	resolverIDs := e.config.ResolverIDs
	if resolverIDs == nil {
		for _, resolver := range testbed.Resolvers {
			resolverIDs = append(resolverIDs, resolver.ID)
		}
	}
	zoneConfigurations, err := os.ReadDir(e.config.ZonesDir)
	if err != nil {
		return err
	}
	bar := progressbar.Default(
		int64(
			len(resolverIDs)*
				len(zoneConfigurations)*
				len(e.config.Delay)*
				len(e.config.Queries),
		),
		fmt.Sprintf("run %s experiment", e.config.Name),
	)
	for _, resolverID := range resolverIDs {
		resolver, err := testbed.FindResolver(resolverID)
		if err != nil {
			return err
		}
		if err := resolver.SetConfig(e.config.QMin, true); err != nil {
			return err
		}
		for _, zoneConfig := range zoneConfigurations {
			if strings.HasPrefix(zoneConfig.Name(), ".") {
				err := bar.Add(len(e.config.Delay))
				if err != nil {
					return err
				}
				continue
			}
			testbed.SetZoneFiles(filepath.Join(e.config.ZonesDir, zoneConfig.Name()))
			for _, delay := range e.config.Delay {
				testbed.SetDelay(time.Duration(delay)*time.Millisecond, e.config.DelayedZones)
				for _, query := range e.config.Queries {
					err := testbed.Flush()
					if err != nil {
						return err
					}
					if e.config.Warmup != nil {
						e.warmup(testbed, resolverID)
					}
					testbed.FlushQueryLogs()
					testbed.Query(resolverID, query.Zone, query.Record)
					result, _ := testbed.Measure(isVolume, isDuration, e.config.Target, e.config.Timeout)
					dataResolver = append(dataResolver, resolverID)
					dataZone = append(dataZone, zoneConfig.Name())
					dataDelay = append(dataDelay, delay)
					dataResult = append(dataResult, int(result))
					dataQuery = append(dataQuery, fmt.Sprintf("%s %s", query.Zone, query.Record))
					if e.config.SaveLogs {
						currentLogDir := filepath.Join(
							logDir,
							fmt.Sprintf(
								"r-%s-z-%s-d-%d-q-%s-qmin-%t",
								resolverID,
								zoneConfig.Name(),
								delay,
								query,
								e.config.QMin,
							),
						)
						if err := os.Mkdir(currentLogDir, perm); err != nil {
							return err
						}
						testbed.SaveLogs(resolverID, currentLogDir)
					}
					err = bar.Add(1)
					if err != nil {
						return err
					}
				}
			}
		}
	}
	dfResult := dataframe.New(
		series.New(dataResolver, series.String, "resolver"),
		series.New(dataZone, series.String, "zone"),
		series.New(dataDelay, series.Int, "delay"),
		series.New(dataResult, series.Int, "result"),
		series.New(dataQuery, series.String, "query"),
	)
	resultsFile, err := os.Create(
		filepath.Join(e.config.Dest, "data.csv"),
	)
	if err != nil {
		return err
	}
	if err := dfResult.WriteCSV(resultsFile); err != nil {
		return err
	}
	return nil
}

func (e *Experiment) warmup(testbed *testbed.Testbed, resolverID string) {
	for _, qname := range e.config.Warmup {
		for i := 0; i < 3; i++ {
			testbed.Query(resolverID, qname, "A")
		}
	}
	time.Sleep(1 * time.Second)
	testbed.FlushQueryLogs()
}
