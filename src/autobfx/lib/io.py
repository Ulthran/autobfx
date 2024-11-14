from pathlib import Path


class IOObject:
    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)

    def __dict__(self):
        return {"fp": str(self.fp)}

    def check(self) -> bool:
        return self.fp.exists()


class IOReads(IOObject):
    def __init__(self, fp: str | Path, r2: str | Path = None):
        super().__init__(fp)
        self.r2 = Path(r2) if r2 else None

    def __dict__(self):
        return {"fp": str(self.fp), "r2": str(self.r2)}

    def check(self) -> bool:
        return self.fp.exists() and (not self.r2 or self.r2.exists())

    def get_output_reads(self, output_fp: Path) -> "IOReads":
        """A function to get the paths for output reads given the corresponding input reads and the directory of the outputs

        Args:
            output_fp (Path): The directory to the output reads

        Returns:
            IOReads: Output reads
        """
        return (
            IOReads(output_fp / self.fp.name, output_fp / self.r2.name)
            if self.r2
            else IOReads(output_fp / self.fp.name)
        )
