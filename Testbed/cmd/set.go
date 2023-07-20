package cmd

import (
	"github.com/spf13/cobra"
	"testbed/config"
	"testbed/testbed"
)

var qmin bool

var cmdSet = &cobra.Command{
	Use:     "set",
	Short:   "Set parameters of resolver configurations",
	Example: "testbed set --qmin=true",
	RunE: func(cmd *cobra.Command, args []string) error {
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		testbed.New(testbedConfig).SetQMIN(qmin)
		return nil
	},
}

func init() {
	cmdSet.Flags().BoolVar(&qmin, "qmin", false, "Enable / disable qname minimization for all resolvers")
	cmdSet.MarkFlagRequired("qmin")
}
