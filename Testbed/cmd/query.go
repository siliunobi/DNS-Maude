package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"testbed/config"
	"testbed/testbed"
	"time"
)

var duration bool
var volume bool
var target string
var timeout time.Duration

var cmdQuery = &cobra.Command{
	Use:     "query [resolver id, qname, record type]",
	Short:   "Query a resolver for a specific qname and record",
	Example: "testbed query resolver-bind-9.18.4 a1.target.com A -v -t target-com",
	Args:    cobra.ExactArgs(3),
	RunE: func(cmd *cobra.Command, args []string) error {
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		t := testbed.New(testbedConfig)
		if _, err := t.FindResolver(args[0]); err != nil {
			return err
		}
		t.Query(args[0], args[1], args[2])
		if duration || volume {
			if target != "" {
				result, unit := t.Measure(volume, duration, target, timeout)
				fmt.Println(result, unit)
			} else {
				fmt.Println("target flag must be provided")
			}
		}
		return nil
	},
}

func init() {
	cmdQuery.Flags().BoolVarP(&duration, "duration", "d", false, "Return duration between first and last query at target")
	cmdQuery.Flags().BoolVarP(&volume, "volume", "v", false, "Return number of queries at target")
	cmdQuery.Flags().StringVarP(&target, "target", "t", "", "Target (required if duration of volume is set)")
	cmdQuery.MarkFlagsMutuallyExclusive("duration", "volume")
	cmdQuery.Flags().DurationVarP(&timeout, "timeout", "o", 0, "Timeout (ms) to wait for further queries")
}
