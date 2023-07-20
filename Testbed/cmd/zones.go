package cmd

import (
	"errors"
	"fmt"
	"github.com/spf13/cobra"
	"os"
	"testbed/config"
	"testbed/testbed"
)

var cmdZones = &cobra.Command{
	Use:     "zones [directory with zone files (named after id of zone, e.g. target-com.zone)]",
	Short:   "Set zone files",
	Example: "testbed zones validation/zones/CNAME+scrubbing/14",
	Args:    cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		fileInfo, err := os.Stat(args[0])
		if err == os.ErrNotExist {
			return err
		}
		if !fileInfo.IsDir() {
			return errors.New(fmt.Sprintf("%s is not a directory", args[0]))
		}
		entries, err := os.ReadDir(args[0])
		if err != nil {
			return err
		}
		for _, entry := range entries {
			if entry.IsDir() {
				fmt.Println("Provide directory with zone files only.")
				return nil
			}
		}
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		t := testbed.New(testbedConfig)
		t.SetDefaultZones()
		t.SetZoneFiles(args[0])
		return nil
	},
}
