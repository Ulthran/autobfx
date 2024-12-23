from autobfx.lib.io import IOObject, IOReads
from pathlib import Path


class AutobfxIterator:
    def __init__(self, name: str, iterable: dict[str, IOObject]):
        self.name = name
        self.iterable = iterable

    def __iter__(self):
        return iter(self.iterable.items())

    def __str__(self):
        return f"{self.name}: {self.iterable}"

    @classmethod
    def gather(
        cls,
        name: str,
        iterable: dict[str, IOObject],
        override: "AutobfxIterator" = None,
    ):
        if override:
            return override

        return AutobfxIterator(name, iterable)


class SampleIterator(AutobfxIterator):
    def __init__(self, samples: dict[str, IOReads]):
        super().__init__("sample", samples)

    @classmethod
    def gather_samples(
        cls,
        fp: Path,
        paired_end: bool,
        config_samples: dict[str, tuple[Path, ...]] = None,
        sample_iterator: "SampleIterator" = None,
    ):
        """
        Gather samples from a directory of fastq files
        The default behavior is to look for fastq files in the directory and assume that the sample name is the part of the filename before '_R1' or '.fastq.gz'
        If a value for `samples` is provided from the config, it will use that instead
        If a SampleIterator has already been created by a flow using this one, it will use the prebuilt one
        """
        if config_samples:
            return cls({n: IOReads(*fps) for n, fps in config_samples.items()})
        elif sample_iterator:
            return sample_iterator
        elif paired_end:
            r1 = [x.resolve() for x in fp.glob("*.fastq.gz") if "_R1" in x.name]
            r2 = [x.resolve() for x in fp.glob("*.fastq.gz") if "_R2" in x.name]
            sample_names = [x.name.split("_R1")[0] for x in r1]
            sample_names_2 = [x.name.split("_R2")[0] for x in r2]
            if sample_names != sample_names_2:
                print(sample_names)
                print(sample_names_2)
                raise ValueError(f"Sample names do not match in {fp}")
            if len(sample_names) != len(set(sample_names)):
                print(sample_names)
                raise ValueError(
                    f"Duplicate sample names in {fp} (Only what's in front of '_R1'/'_R2' is considered)"
                )

            if len(r1) != len(r2):
                print(r1)
                print(r2)
                raise ValueError(f"Number of R1 and R2 files do not match in {fp}")

            return SampleIterator(
                {x: IOReads(y, z) for x, y, z in zip(sample_names, r1, r2)}
            )
        else:
            r1 = list(fp.glob("*.fastq.gz"))
            sample_names = [x.name.split(".fastq")[0] for x in r1]
            if len(sample_names) != len(set(sample_names)):
                print(sample_names)
                raise ValueError(f"Duplicate sample names in {fp}")

            return SampleIterator({x: IOReads(y) for x, y in zip(sample_names, r1)})
