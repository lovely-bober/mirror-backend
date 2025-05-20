from celery import shared_task


class VoiceReconService():
    @shared_task(ignore_result=False)
    def add_together(a: int, b: int) -> int:
        return a + b