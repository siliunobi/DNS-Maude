package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"os"
	"path/filepath"
	"testbed/config"
	"testbed/experiment"
	"time"
)

var runAll bool

var cmdRun = &cobra.Command{
	Use:     "run [experiment config]",
	Short:   "Run an experiment according to the specified configuration",
	Example: "run validation/experiments/subquery+CNAME.yaml",
	Args:    cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		configStat, err := os.Stat(args[0])
		if err != nil {
			return nil
		}
		if runAll {
			if !configStat.IsDir() {
				fmt.Println("must provide directory when running with -a")
			}
			configEntries, err := os.ReadDir(args[0])
			if err != nil {
				return err
			}
			for _, entry := range configEntries {
				configPath := filepath.Join(args[0], entry.Name())
				if err := runExperiment(configPath); err != nil {
					fmt.Printf("cannot run experiment with configuration %s\n", configPath)
					return err
				}
			}
		}
		if err := runExperiment(args[0]); err != nil {
			fmt.Printf("cannot run experiment with configuration %s\n", args[0])
			return err
		}
		return nil
	},
}

func runExperiment(experimentConfigPath string) error {
	experimentConfig, err := config.New().LoadExperimentConfig(experimentConfigPath)
	if err != nil {
		return err
	}
	t, err := initTestbed(experimentConfig.Testbed)
	if err != nil {
		return err
	}
	t.Start()
	time.Sleep(1 * time.Second)
	if err := experiment.New(experimentConfig).Run(t); err != nil {
		return err
	}
	fmt.Printf("results written to %s\n", experimentConfig.Dest)
	return nil
}

func init() {
	cmdRun.Flags().BoolVarP(&runAll, "runAll", "a", false, "Run all experiments at configuration location")
}
