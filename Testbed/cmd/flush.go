package cmd

import (
	"github.com/spf13/cobra"
	"testbed/config"
	"testbed/testbed"
)

var cmdFlush = &cobra.Command{
	Use:     "flush",
	Short:   "Flush the cache of all resolvers",
	Example: "testbed flush",
	Args:    cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) error {
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		return testbed.New(testbedConfig).Flush()
	},
}
